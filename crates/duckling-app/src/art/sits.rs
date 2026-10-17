//! SITS (Student Information Technology Services) branding & logo rendering.
//!
//! Refurbishing old tech, educating consumers, and donating computers to
//! families and students in need (Canton CV 26).

use eframe::egui::epaint::Mesh;
use eframe::egui::{
    self, Color32, Context, Id, Painter, Pos2, Rect, Shape, TextureHandle, TextureOptions, vec2,
};

pub const SITS_LOGO_PNG: &[u8] = include_bytes!("sits_logo.png");

/// SITS vibrant colors from logoGray.svg
pub const BLUE: Color32 = Color32::from_rgb(69, 167, 245);
pub const PURPLE: Color32 = Color32::from_rgb(128, 50, 231);
pub const PINK: Color32 = Color32::from_rgb(247, 79, 217);
#[allow(dead_code)]
pub const GRAY: Color32 = Color32::from_rgb(214, 215, 217);
pub const DUCK_GOLD: Color32 = Color32::from_rgb(255, 198, 41);
#[allow(dead_code)]
pub const AMBER: Color32 = DUCK_GOLD;

/// Cached texture handle for the SITS logo.
pub fn logo_texture(ctx: &Context) -> TextureHandle {
    let id = Id::new("sits-logo-texture");
    ctx.data_mut(|d| d.get_temp::<TextureHandle>(id))
        .unwrap_or_else(|| {
            let image = if let Ok(dyn_img) = image::load_from_memory(SITS_LOGO_PNG) {
                let rgba = dyn_img.to_rgba8();
                let size = [rgba.width() as usize, rgba.height() as usize];
                egui::ColorImage::from_rgba_unmultiplied(size, rgba.as_raw())
            } else {
                egui::ColorImage::example()
            };
            let handle = ctx.load_texture("sits-brand-logo", image, TextureOptions::LINEAR);
            ctx.data_mut(|d| d.insert_temp(id, handle.clone()));
            handle
        })
}

/// Draws the SITS logo preserving its natural aspect ratio within `rect`.
pub fn logo(ctx: &Context, painter: &Painter, rect: Rect) {
    let texture = logo_texture(ctx);
    let aspect = 640.0 / 289.0;
    let mut w = rect.width();
    let mut h = w / aspect;
    if h > rect.height() {
        h = rect.height();
        w = h * aspect;
    }
    let dest = Rect::from_center_size(rect.center(), vec2(w, h));
    let uv = Rect::from_min_max(Pos2::ZERO, egui::pos2(1.0, 1.0));
    let mut mesh = Mesh::with_texture(texture.id());
    mesh.add_rect_with_uv(dest, uv, Color32::WHITE);
    painter.add(Shape::mesh(mesh));
}
