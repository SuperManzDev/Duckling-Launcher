// Dependency-free app icon rasterizer. Shared by the app (window icon) and
// `build.rs` (the .exe icon) via `include!`, so it must not use crates.
//
// The Duckling mark: a cheerful, golden-yellow duckling with an orange bill,
// glossy eye with highlight, wing depth and soft warm shading. Bold and clean
// enough to stay crisp at 16px.

/// Supersampling grid per axis (SS × SS samples per pixel).
const SS: u32 = 4;

/// RGBA (unpremultiplied) icon, `size`×`size`.
pub fn app_icon_rgba(size: u32) -> Vec<u8> {
    let n = size as f32;
    let mut rgba = Vec::with_capacity((size * size * 4) as usize);
    for y in 0..size {
        for x in 0..size {
            let mut hits = 0u32;
            let mut r_acc = 0.0f32;
            let mut g_acc = 0.0f32;
            let mut b_acc = 0.0f32;
            for sy in 0..SS {
                for sx in 0..SS {
                    // Sample position relative to the center, in icon units (-0.5 to 0.5).
                    let u = (x as f32 + (sx as f32 + 0.5) / SS as f32) / n - 0.5;
                    let v = (y as f32 + (sy as f32 + 0.5) / SS as f32) / n - 0.5;
                    if let Some((r, g, b)) = sample_duck(u, v) {
                        hits += 1;
                        r_acc += r;
                        g_acc += g;
                        b_acc += b;
                    }
                }
            }
            if hits > 0 {
                let coverage = hits as f32 / (SS * SS) as f32;
                let r = (r_acc / hits as f32).clamp(0.0, 255.0) as u8;
                let g = (g_acc / hits as f32).clamp(0.0, 255.0) as u8;
                let b = (b_acc / hits as f32).clamp(0.0, 255.0) as u8;
                let a = (coverage * 255.0).clamp(0.0, 255.0) as u8;
                rgba.extend_from_slice(&[r, g, b, a]);
            } else {
                rgba.extend_from_slice(&[0, 0, 0, 0]);
            }
        }
    }
    rgba
}

fn smin(a: f32, b: f32, k: f32) -> f32 {
    let h = (k - (a - b).abs()).max(0.0) / k;
    a.min(b) - h * h * k * 0.25
}

fn dist_circle(px: f32, py: f32, cx: f32, cy: f32, r: f32) -> f32 {
    let dx = px - cx;
    let dy = py - cy;
    (dx * dx + dy * dy).sqrt() - r
}

fn dist_segment(px: f32, py: f32, ax: f32, ay: f32, bx: f32, by: f32) -> f32 {
    let (abx, aby) = (bx - ax, by - ay);
    let len_sq = (abx * abx + aby * aby).max(1e-8);
    let t = (((px - ax) * abx + (py - ay) * aby) / len_sq).clamp(0.0, 1.0);
    let (qx, qy) = (ax + abx * t - px, ay + aby * t - py);
    (qx * qx + qy * qy).sqrt()
}

fn point_in_polygon(x: f32, y: f32, poly: &[(f32, f32)]) -> bool {
    let mut inside = false;
    let mut j = poly.len() - 1;
    for i in 0..poly.len() {
        let (xi, yi) = poly[i];
        let (xj, yj) = poly[j];
        if (yi > y) != (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi {
            inside = !inside;
        }
        j = i;
    }
    inside
}

const BEAK_POLY: [(f32, f32); 6] = [
    (0.19, -0.16),
    (0.37, -0.14),
    (0.42, -0.10),
    (0.39, -0.06),
    (0.20, -0.06),
    (0.17, -0.10),
];

const TAIL_POLY: [(f32, f32); 4] = [(-0.16, 0.05), (-0.39, -0.06), (-0.34, 0.08), (-0.25, 0.20)];

fn sample_duck(u: f32, v: f32) -> Option<(f32, f32, f32)> {
    let d_head = dist_circle(u, v, 0.07, -0.15, 0.19);

    let bu = u - (-0.05);
    let bv = (v - 0.14) / 0.75;
    let d_body = (bu * bu + bv * bv).sqrt() - 0.27;

    let in_tail = point_in_polygon(u, v, &TAIL_POLY);
    let d_tail = dist_segment(u, v, -0.18, 0.10, -0.37, -0.04) - 0.045;

    let d_body_tail = d_body.min(d_tail);
    let d_yellow = smin(d_head, d_body_tail, 0.08);

    let in_beak = point_in_polygon(u, v, &BEAK_POLY);
    let d_beak = dist_segment(u, v, 0.19, -0.11, 0.37, -0.10) - 0.052;

    let d_eye = dist_circle(u, v, 0.16, -0.20, 0.040);
    let d_glint1 = dist_circle(u, v, 0.175, -0.215, 0.015);
    let d_glint2 = dist_circle(u, v, 0.146, -0.190, 0.007);

    // Wing oval on flank
    let wu = (u - (-0.04)) * 0.96 - (v - 0.13) * 0.26;
    let wv = (u - (-0.04)) * 0.26 + (v - 0.13) * 0.96;
    let d_wing = (wu * wu / (0.16 * 0.16) + wv * wv / (0.10 * 0.10)).sqrt() - 1.0;

    let d_blush = dist_circle(u, v, 0.18, -0.09, 0.045);

    if d_beak <= 0.0 || in_beak {
        let t = ((u - 0.18) / 0.24).clamp(0.0, 1.0);
        let mut r = 249.0 - 20.0 * t;
        let mut g = 120.0 - 40.0 * t;
        let b = 20.0;

        let beak_line_dist = (v - (-0.105)).abs();
        if beak_line_dist < 0.012 && u >= 0.20 && u <= 0.36 {
            let factor = 1.0 - (beak_line_dist / 0.012);
            r -= 40.0 * factor;
            g -= 45.0 * factor;
        }
        return Some((r.max(0.0), g.max(0.0), b));
    }

    if d_yellow <= 0.0 || in_tail {
        if d_eye <= 0.0 {
            if d_glint1 <= 0.0 || d_glint2 <= 0.0 {
                return Some((255.0, 255.0, 255.0));
            }
            return Some((24.0, 24.0, 27.0));
        }

        let vert_t = ((v + 0.3) / 0.65).clamp(0.0, 1.0);
        let (mut r, mut g, mut b) = if vert_t < 0.4 {
            let k = vert_t / 0.4;
            (
                254.0 + (251.0 - 254.0) * k,
                240.0 + (191.0 - 240.0) * k,
                138.0 + (36.0 - 138.0) * k,
            )
        } else {
            let k = (vert_t - 0.4) / 0.6;
            (
                251.0 + (234.0 - 251.0) * k,
                191.0 + (138.0 - 191.0) * k,
                36.0 + (8.0 - 36.0) * k,
            )
        };

        if d_wing <= 0.0 {
            let wing_depth = (-d_wing / 0.5).min(1.0);
            r -= 12.0 * wing_depth;
            g -= 24.0 * wing_depth;
            b += 8.0 * wing_depth;
        }

        if d_wing >= -0.12 && d_wing <= 0.06 {
            let wing_border = 1.0 - (d_wing + 0.03).abs() / 0.09;
            r -= 35.0 * wing_border;
            g -= 50.0 * wing_border;
            b -= 5.0 * wing_border;
        }

        if d_blush <= 0.0 {
            let blush_k = (-d_blush / 0.045).max(0.0);
            r = r + (255.0 - r) * blush_k * 0.45;
            g = g * (1.0 - blush_k * 0.18);
            b = b * (1.0 - blush_k * 0.28);
        }

        return Some((
            r.clamp(0.0, 255.0),
            g.clamp(0.0, 255.0),
            b.clamp(0.0, 255.0),
        ));
    }

    None
}

/// Windows .ico with 32-bit BMP images at the given sizes.
#[allow(dead_code)]
pub fn ico_bytes(sizes: &[u32]) -> Vec<u8> {
    let images: Vec<Vec<u8>> = sizes.iter().map(|&s| bmp_entry(s)).collect();
    let mut out = Vec::new();
    out.extend_from_slice(&[0, 0, 1, 0]);
    out.extend_from_slice(&(sizes.len() as u16).to_le_bytes());
    let mut offset = 6 + 16 * sizes.len() as u32;
    for (&size, image) in sizes.iter().zip(&images) {
        let dim = if size >= 256 { 0 } else { size as u8 };
        out.extend_from_slice(&[dim, dim, 0, 0, 1, 0, 32, 0]);
        out.extend_from_slice(&(image.len() as u32).to_le_bytes());
        out.extend_from_slice(&offset.to_le_bytes());
        offset += image.len() as u32;
    }
    for image in images {
        out.extend_from_slice(&image);
    }
    out
}

/// BITMAPINFOHEADER + bottom-up BGRA pixels + (empty) AND mask.
fn bmp_entry(size: u32) -> Vec<u8> {
    let rgba = app_icon_rgba(size);
    let mask_row = size.div_ceil(32) * 4;
    let mut out = Vec::new();
    out.extend_from_slice(&40u32.to_le_bytes());
    out.extend_from_slice(&(size as i32).to_le_bytes());
    out.extend_from_slice(&(size as i32 * 2).to_le_bytes());
    out.extend_from_slice(&1u16.to_le_bytes());
    out.extend_from_slice(&32u16.to_le_bytes());
    out.extend_from_slice(&[0u8; 24]);
    for y in (0..size).rev() {
        for x in 0..size {
            let i = ((y * size + x) * 4) as usize;
            out.extend_from_slice(&[rgba[i + 2], rgba[i + 1], rgba[i], rgba[i + 3]]);
        }
    }
    out.extend(std::iter::repeat_n(0u8, (mask_row * size) as usize));
    out
}
