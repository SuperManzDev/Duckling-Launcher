//! Drifting golden embers and fireflies with depth: far ones are soft dots,
//! near ones have a bright glowing core.

use std::f32::consts::TAU;

use eframe::egui::{Color32, Painter, Rect, pos2};

use crate::art::hash01;

const MOTE_COUNT: u32 = 80;
/// Particles with depth above this are drawn with a bright glow core.
const GLOW_DEPTH: f32 = 0.84;

pub fn paint(painter: &Painter, rect: Rect, t: f32, mote_color: Color32) {
    let span = rect.height() + 20.0;
    for i in 0..MOTE_COUNT {
        let depth = hash01(i, 7);
        let speed = 10.0 + depth * 32.0;
        let y = (hash01(i, 8) * span + t * speed) % span - 10.0;
        let sway = (t * (0.4 + depth) + hash01(i, 9) * TAU).sin() * (4.0 + 12.0 * depth);
        let pos = pos2(
            rect.left() + hash01(i, 10) * rect.width() + sway,
            rect.top() + y,
        );
        let color = mote_color.gamma_multiply(0.25 + 0.6 * depth);
        if depth > GLOW_DEPTH {
            let radius = 2.0 + 1.5 * hash01(i, 11);
            painter.circle_filled(pos, radius, color);
            painter.circle_filled(
                pos,
                radius * 0.45,
                Color32::WHITE.gamma_multiply(0.75 * depth),
            );
        } else {
            painter.circle_filled(pos, 0.6 + depth * 1.5, color);
        }
    }
}
