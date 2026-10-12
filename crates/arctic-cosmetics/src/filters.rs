//! Parsing what the admin lists can be narrowed by: dates and launcher
//! versions as people type them.

use std::cmp::Ordering;

/// A day (`2026-10-10`, midnight UTC) or a Unix time in seconds.
pub fn parse_since(text: &str) -> Option<i64> {
    let text = text.trim();
    if let Ok(seconds) = text.parse::<i64>() {
        return (seconds >= 0).then_some(seconds);
    }
    let mut parts = text.splitn(3, '-').map(str::parse::<i64>);
    let (year, month, day) = (
        parts.next()?.ok()?,
        parts.next()?.ok()?,
        parts.next()?.ok()?,
    );
    if !(1970..=9999).contains(&year) || !(1..=12).contains(&month) || !(1..=31).contains(&day) {
        return None;
    }
    Some(days_from_civil(year, month, day) * 86_400)
}

/// Days since 1970-01-01 (Howard Hinnant's `days_from_civil`).
fn days_from_civil(year: i64, month: i64, day: i64) -> i64 {
    let year = if month <= 2 { year - 1 } else { year };
    let era = year.div_euclid(400);
    let year_of_era = year - era * 400;
    let month_index = (month + 9) % 12;
    let day_of_year = (153 * month_index + 2) / 5 + day - 1;
    let day_of_era = year_of_era * 365 + year_of_era / 4 - year_of_era / 100 + day_of_year;
    era * 146_097 + day_of_era - 719_468
}

/// `0.3.4`, `v0.3.4` or `0.3.4-beta` as numbers; `None` for anything else
/// (a development build sends no version).
fn version_parts(text: &str) -> Option<Vec<u64>> {
    let text = text.trim().trim_start_matches('v');
    let core = text.split(['-', '+', ' ']).next()?;
    let parts = core
        .split('.')
        .map(|p| p.parse::<u64>().ok())
        .collect::<Option<Vec<_>>>()?;
    (!parts.is_empty()).then_some(parts)
}

pub fn is_version(text: &str) -> bool {
    version_parts(text).is_some()
}

/// Versions newest first, then anything that isn't a version (in text order).
pub fn sort_newest_first(items: &mut [String]) {
    items.sort_by(|a, b| match (version_parts(a), version_parts(b)) {
        (Some(x), Some(y)) => compare_versions(b, a)
            .unwrap_or(Ordering::Equal)
            .then_with(|| x.len().cmp(&y.len()))
            .then_with(|| a.cmp(b)),
        (Some(_), None) => Ordering::Less,
        (None, Some(_)) => Ordering::Greater,
        (None, None) => a.cmp(b),
    });
}

/// How two launcher versions compare, when both are versions.
pub fn compare_versions(a: &str, b: &str) -> Option<Ordering> {
    let (mut a, mut b) = (version_parts(a)?, version_parts(b)?);
    let len = a.len().max(b.len());
    a.resize(len, 0);
    b.resize(len, 0);
    Some(a.cmp(&b))
}

/// The highest version in the list (ones that aren't versions are skipped).
pub fn newest_version<'a>(versions: impl IntoIterator<Item = &'a str>) -> Option<&'a str> {
    versions.into_iter().fold(None, |best, v| match best {
        None if version_parts(v).is_some() => Some(v),
        Some(b) if compare_versions(v, b) == Some(Ordering::Greater) => Some(v),
        other => other,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn days_and_seconds_are_both_accepted() {
        assert_eq!(parse_since("1970-01-01"), Some(0));
        assert_eq!(parse_since("2026-10-10"), Some(1_791_590_400));
        assert_eq!(parse_since(" 1791590400 "), Some(1_791_590_400));
        assert_eq!(parse_since("2026-13-01"), None);
        assert_eq!(parse_since("yesterday"), None);
        assert_eq!(parse_since("-5"), None);
    }

    #[test]
    fn versions_compare_by_number() {
        assert_eq!(compare_versions("0.3.10", "0.3.9"), Some(Ordering::Greater));
        assert_eq!(compare_versions("v0.3", "0.3.0"), Some(Ordering::Equal));
        assert_eq!(
            compare_versions("0.3.4-beta", "0.3.5"),
            Some(Ordering::Less)
        );
        assert_eq!(compare_versions("", "0.3.5"), None);
        assert_eq!(
            newest_version(["0.3.4", "dev", "0.3.10", "0.3.9"]),
            Some("0.3.10")
        );
        assert_eq!(newest_version(["dev", ""]), None);
        assert!(is_version("0.3.5") && !is_version("next release") && !is_version("0,3,5"));
        let mut mixed: Vec<String> = ["dev", "0.3.4", "", "0.3.10", "v0.3.4", "beta"]
            .map(String::from)
            .to_vec();
        sort_newest_first(&mut mixed);
        assert_eq!(mixed, ["0.3.10", "0.3.4", "v0.3.4", "", "beta", "dev"]);
    }
}
