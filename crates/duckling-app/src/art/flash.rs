//! Supporter branding: SITS (Student Information Technology Services).

pub use super::sits::*;

use eframe::egui::{Align2, Color32, FontId, Painter, Rect, Stroke};

/// Vector fallback mark when an egui Context is not directly provided.
#[allow(dead_code)]
pub fn mark(painter: &Painter, rect: Rect) {
    let r = 6.0;
    // SITS gradient base tile
    painter.rect_filled(rect, r, BLUE);
    let inner = rect.shrink(2.0);
    painter.rect_filled(inner, r - 1.0, Color32::from_rgb(26, 32, 44));
    painter.rect_stroke(
        rect,
        r,
        Stroke::new(1.0, PURPLE),
        eframe::egui::StrokeKind::Inside,
    );
    // Draw "SITS" text or duck glyph in the mark
    painter.text(
        rect.center(),
        Align2::CENTER_CENTER,
        "SITS",
        FontId::proportional((rect.height() * 0.44).max(8.0)),
        DUCK_GOLD,
    );
}
