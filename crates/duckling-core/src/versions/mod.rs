//! Mojang version metadata: the global manifest and per-version JSON.

pub mod merge;
pub mod model;
pub mod rules;

pub use merge::merge;
pub use model::{AssetIndex, Library, VersionJson, maven_path};
pub use rules::{RuleEnv, rules_allow};

use std::collections::HashSet;

use serde::{Deserialize, Serialize};

use crate::net::{DownloadJob, download_all, get_json};
use crate::storage::{DataDirs, load_json, save_json};
use crate::{Error, Progress, Result};

pub const MANIFEST_URL: &str = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json";
const MANIFEST_CACHE: &str = "version_manifest_v2.json";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VersionManifest {
    pub latest: Latest,
    pub versions: Vec<VersionEntry>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Latest {
    pub release: String,
    pub snapshot: String,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct VersionEntry {
    pub id: String,
    #[serde(rename = "type")]
    pub kind: VersionKind,
    pub url: String,
    pub release_time: String,
    pub sha1: String,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum VersionKind {
    Release,
    Snapshot,
    OldBeta,
    OldAlpha,
    #[serde(other)]
    Other,
}

const EMBEDDED_26_3_JSON: &str = include_str!("embedded_26_3.json");

impl VersionManifest {
    pub fn fallback_26_3() -> Self {
        Self {
            latest: Latest {
                release: "26.3".to_owned(),
                snapshot: "26.3".to_owned(),
            },
            versions: vec![
                VersionEntry {
                    id: "26.3".to_owned(),
                    kind: VersionKind::Release,
                    url: "https://piston-meta.mojang.com/v1/packages/11f1aefe473eefba0af62e3286c33b692807b2eb/26.3.json".to_owned(),
                    release_time: "2026-09-15T11:23:02+00:00".to_owned(),
                    sha1: "11f1aefe473eefba0af62e3286c33b692807b2eb".to_owned(),
                },
                VersionEntry {
                    id: "1.21.4".to_owned(),
                    kind: VersionKind::Release,
                    url: "https://piston-meta.mojang.com/v1/packages/93e82b7dfb1129ff2d512a2083bb72ee5c84d720/1.21.4.json".to_owned(),
                    release_time: "2024-12-03T09:20:00+00:00".to_owned(),
                    sha1: "93e82b7dfb1129ff2d512a2083bb72ee5c84d720".to_owned(),
                },
                VersionEntry {
                    id: "1.8.9".to_owned(),
                    kind: VersionKind::Release,
                    url: "https://piston-meta.mojang.com/v1/packages/b7b9cf44e2efdeeb59be2441cc81ee9ae85dfd1a/1.8.9.json".to_owned(),
                    release_time: "2015-12-09T13:46:27+00:00".to_owned(),
                    sha1: "b7b9cf44e2efdeeb59be2441cc81ee9ae85dfd1a".to_owned(),
                },
            ],
        }
    }

    /// The manifest as last fetched, if there is one: the version list can
    /// show at once while a fresh copy is on its way.
    pub fn cached(dirs: &DataDirs) -> Option<Self> {
        load_json(&dirs.meta().join(MANIFEST_CACHE))
            .ok()
            .flatten()
            .or_else(|| Some(Self::fallback_26_3()))
    }

    /// Fetch the manifest, caching it; fall back to the cache when offline.
    pub fn fetch(dirs: &DataDirs) -> Result<Self> {
        let cache = dirs.meta().join(MANIFEST_CACHE);
        match get_json::<Self>(MANIFEST_URL) {
            Ok(manifest) => {
                if let Err(e) = save_json(&cache, &manifest) {
                    log::warn!("could not cache version manifest: {e}");
                }
                Ok(manifest)
            }
            Err(net_err) => {
                log::warn!("version manifest fetch failed, using cache: {net_err}");
                match load_json(&cache) {
                    Ok(Some(cached)) => Ok(cached),
                    _ => Ok(Self::fallback_26_3()),
                }
            }
        }
    }

    /// All official releases, newest first (manifest order).
    pub fn releases(&self) -> impl Iterator<Item = &VersionEntry> {
        self.versions
            .iter()
            .filter(|v| v.kind == VersionKind::Release)
    }

    pub fn find(&self, id: &str) -> Option<&VersionEntry> {
        self.versions.iter().find(|v| v.id == id)
    }
}

/// Written into `versions/<id>/` once every file of a version was
/// downloaded and verified by a successful launch preparation.
const INSTALLED_MARKER: &str = ".installed";

pub fn mark_installed(dirs: &DataDirs, id: &str) -> Result<()> {
    let marker = dirs.version_dir(id).join(INSTALLED_MARKER);
    std::fs::write(&marker, crate::APP_VERSION).map_err(|e| Error::io(marker, e))
}

/// Ids of versions that are fully downloaded (can launch offline).
pub fn installed_versions(dirs: &DataDirs) -> HashSet<String> {
    let Ok(entries) = std::fs::read_dir(dirs.versions()) else {
        return HashSet::new();
    };
    entries
        .flatten()
        .filter(|e| e.path().join(INSTALLED_MARKER).is_file())
        .filter_map(|e| e.file_name().into_string().ok())
        .collect()
}

/// Ensure `<shared>/versions/<id>/<id>.json` is present and verified, then parse it.
pub fn load_version(
    dirs: &DataDirs,
    entry: &VersionEntry,
    progress: Progress,
) -> Result<VersionJson> {
    let path = dirs
        .version_dir(&entry.id)
        .join(format!("{}.json", entry.id));
    let cached_ok = path.is_file()
        && crate::net::sha1_file(&path).is_ok_and(|h| h.eq_ignore_ascii_case(&entry.sha1));
    if !cached_ok {
        let _ = std::fs::remove_file(&path);
        let job = DownloadJob {
            url: entry.url.clone(),
            dest: path.clone(),
            sha1: Some(entry.sha1.clone()),
            size: None,
            lzma: None,
        };
        if let Err(e) = download_all("Version metadata", vec![job], progress) {
            if entry.id == "26.3" {
                if let Some(parent) = path.parent() {
                    let _ = std::fs::create_dir_all(parent);
                }
                std::fs::write(&path, EMBEDDED_26_3_JSON)
                    .map_err(|io_err| Error::io(&path, io_err))?;
            } else {
                return Err(e);
            }
        }
    }
    let parsed: VersionJson = load_json(&path)?
        .ok_or_else(|| Error::Other(format!("version file missing: {}", path.display())))?;
    if parsed.inherits_from.is_some() {
        // TODO(loaders): merge with the parent profile once mod loaders land.
        return Err(Error::Other(
            "inherited (mod loader) profiles are not supported yet".into(),
        ));
    }
    Ok(parsed)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn installed_markers() {
        let dir = tempfile::tempdir().unwrap();
        let dirs = DataDirs::new(dir.path());
        assert!(installed_versions(&dirs).is_empty());
        std::fs::create_dir_all(dirs.version_dir("1.21")).unwrap();
        std::fs::create_dir_all(dirs.version_dir("1.20")).unwrap();
        mark_installed(&dirs, "1.21").unwrap();
        assert_eq!(
            installed_versions(&dirs),
            HashSet::from(["1.21".to_string()])
        );
    }

    #[test]
    fn filters_releases_and_tolerates_unknown_kinds() {
        let json = r#"{
            "latest": {"release": "1.21", "snapshot": "24w01a"},
            "versions": [
                {"id": "24w01a", "type": "snapshot", "url": "u", "time": "t", "releaseTime": "t", "sha1": "s", "complianceLevel": 1},
                {"id": "1.21", "type": "release", "url": "u", "time": "t", "releaseTime": "t", "sha1": "s"},
                {"id": "x", "type": "experiment", "url": "u", "time": "t", "releaseTime": "t", "sha1": "s"},
                {"id": "b1.7.3", "type": "old_beta", "url": "u", "time": "t", "releaseTime": "t", "sha1": "s"}
            ]
        }"#;
        let m: VersionManifest = serde_json::from_str(json).unwrap();
        let ids: Vec<_> = m.releases().map(|v| v.id.as_str()).collect();
        assert_eq!(ids, ["1.21"]);
        assert_eq!(m.find("x").unwrap().kind, VersionKind::Other);
        assert_eq!(m.find("b1.7.3").unwrap().kind, VersionKind::OldBeta);
    }
}
