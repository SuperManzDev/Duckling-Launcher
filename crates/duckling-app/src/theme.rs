//! Color themes. `Default` is the aurora night, `Dark` is a quieter graphite
//! night, `Light` is a daytime arctic. Each palette also drives the painted
//! scenery (`art::scenery`).

use duckling_core::settings::ThemeMode;
use eframe::egui::{self, Color32, CornerRadius, Stroke, Theme};

const fn rgb(hex: u32) -> Color32 {
    Color32::from_rgb((hex >> 16) as u8, (hex >> 8) as u8, hex as u8)
}

/// Unmultiplied `#rrggbb` + alpha, premultiplied at compile time.
const fn rgba(hex: u32, alpha: u8) -> Color32 {
    Color32::from_rgba_premultiplied(
        premultiply(hex >> 16, alpha),
        premultiply(hex >> 8, alpha),
        premultiply(hex, alpha),
        alpha,
    )
}

const fn premultiply(channel: u32, alpha: u8) -> u8 {
    ((channel & 0xff) * alpha as u32 / 255) as u8
}

/// Colors for the painted backdrop.
pub struct Scene {
    /// Sky gradient: top, middle, horizon.
    pub sky: [Color32; 3],
    pub star_strength: f32,
    pub aurora_strength: f32,
    pub snow: Color32,
    /// Ridge outline color (alpha-blended).
    pub rim: Color32,
    pub snow_cap: Color32,
    /// (ridge color, base color) for the far, middle and near layers.
    pub mountains: [(Color32, Color32); 3],
    pub celestial: Celestial,
    /// Haze drawn between mountain layers (alpha-blended).
    pub mist: Color32,
    /// Pine tree silhouettes along the bottom edge.
    pub trees: Color32,
}

/// The body in the sky.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Celestial {
    Moon,
    Sun,
}

pub struct Palette {
    pub dark: bool,
    /// Cards and the sidebar frost the backdrop behind them (see `glass`).
    pub glass: bool,
    pub bg: Color32,
    pub surface: Color32,
    pub surface_hover: Color32,
    pub accent: Color32,
    pub accent_deep: Color32,
    /// Text drawn on top of the accent color (Play button).
    pub on_accent: Color32,
    pub text: Color32,
    pub muted: Color32,
    pub warn: Color32,
    pub error: Color32,
    pub card_fill: Color32,
    pub card_stroke: Color32,
    pub nav_fill: Color32,
    /// Native title bar color (matches the sidebar over the sky). Only
    /// Windows lets apps tint the native title bar.
    #[cfg_attr(not(windows), allow(dead_code))]
    pub titlebar: Color32,
    pub shadow: Color32,
    pub scene: Scene,
}

pub static DEFAULT: Palette = Palette {
    dark: true,
    glass: false,
    bg: rgb(0x111318),
    surface: rgb(0x1a1e26),
    surface_hover: rgb(0x242a36),
    accent: rgb(0xfbbf24),
    accent_deep: rgb(0xf59e0b),
    on_accent: rgb(0x18181b),
    text: rgb(0xfdfbf7),
    muted: rgb(0xa39d93),
    warn: rgb(0xf97316),
    error: rgb(0xf87171),
    card_fill: rgba(0x141720, 215),
    card_stroke: rgba(0xfbbf24, 45),
    nav_fill: rgba(0x0c0d12, 230),
    titlebar: rgb(0x0c0d12),
    shadow: Color32::from_black_alpha(90),
    scene: Scene {
        sky: [rgb(0x0a0c14), rgb(0x161528), rgb(0x2d1f35)],
        star_strength: 0.9,
        aurora_strength: 0.85,
        snow: rgb(0xfde68a),
        rim: rgba(0xfde68a, 60),
        snow_cap: rgba(0xfef3c7, 100),
        mountains: [
            (rgb(0x352b42), rgb(0x1a1624)),
            (rgb(0x231d2e), rgb(0x120f1a)),
            (rgb(0x15121c), rgb(0x0b0910)),
        ],
        celestial: Celestial::Moon,
        mist: rgba(0x352b42, 60),
        trees: rgb(0x08070d),
    },
};

pub static DARK: Palette = Palette {
    dark: true,
    glass: false,
    bg: rgb(0x0e0e11),
    surface: rgb(0x17171d),
    surface_hover: rgb(0x21212a),
    accent: rgb(0xf59e0b),
    accent_deep: rgb(0xd97706),
    on_accent: rgb(0x0e0e11),
    text: rgb(0xf4f4f5),
    muted: rgb(0x9ca3af),
    warn: rgb(0xf97316),
    error: rgb(0xef4444),
    card_fill: rgba(0x121216, 220),
    card_stroke: rgba(0xf59e0b, 35),
    nav_fill: rgba(0x09090b, 235),
    titlebar: rgb(0x09090b),
    shadow: Color32::from_black_alpha(110),
    scene: Scene {
        sky: [rgb(0x060608), rgb(0x0d0d12), rgb(0x171620)],
        star_strength: 0.7,
        aurora_strength: 0.35,
        snow: rgb(0xfde68a),
        rim: rgba(0xfde68a, 40),
        snow_cap: rgba(0xfde68a, 70),
        mountains: [
            (rgb(0x26222c), rgb(0x151219)),
            (rgb(0x1a1720), rgb(0x0e0c12)),
            (rgb(0x100e14), rgb(0x08070a)),
        ],
        celestial: Celestial::Moon,
        mist: rgba(0x26222c, 60),
        trees: rgb(0x08070a),
    },
};

pub static LIGHT: Palette = Palette {
    dark: false,
    glass: false,
    bg: rgb(0xfcfaf6),
    surface: rgb(0xf5eee0),
    surface_hover: rgb(0xebe0ce),
    accent: rgb(0xd97706),
    accent_deep: rgb(0xb45309),
    on_accent: rgb(0xffffff),
    text: rgb(0x1c1917),
    muted: rgb(0x78716c),
    warn: rgb(0xea580c),
    error: rgb(0xdc2626),
    card_fill: rgba(0xffffff, 220),
    card_stroke: rgba(0xd97706, 36),
    nav_fill: rgba(0xfaf5eb, 235),
    titlebar: rgb(0xf5eee0),
    shadow: rgba(0x3f2e1e, 40),
    scene: Scene {
        sky: [rgb(0x60a5fa), rgb(0x93c5fd), rgb(0xfef08a)],
        star_strength: 0.0,
        aurora_strength: 0.0,
        snow: rgb(0xfef08a),
        rim: rgba(0xf59e0b, 90),
        snow_cap: rgba(0xffffff, 230),
        mountains: [
            (rgb(0xa3c9a8), rgb(0x7da883)),
            (rgb(0xbfd8c4), rgb(0x9bbfa2)),
            (rgb(0xd8e8dc), rgb(0xbcd4c1)),
        ],
        celestial: Celestial::Sun,
        mist: rgba(0xffffff, 100),
        trees: rgb(0x4a6b52),
    },
};

/// Aurora's night seen through frosted glass: cards and the sidebar blur what's behind them and
/// tint it only lightly; buttons are glass too.
pub static GLASS: Palette = Palette {
    dark: true,
    glass: true,
    bg: rgb(0x0f1117),
    surface: rgba(0xfde68a, 22),
    surface_hover: rgba(0xfde68a, 40),
    accent: rgb(0xfcd34d),
    accent_deep: rgb(0xf59e0b),
    on_accent: rgb(0x0f1117),
    text: rgb(0xfef9ee),
    muted: rgb(0xb8ad9c),
    warn: rgb(0xf97316),
    error: rgb(0xf87171),
    card_fill: rgba(0x131622, 110),
    card_stroke: rgba(0xfde68a, 48),
    nav_fill: rgba(0x0a0c12, 120),
    titlebar: rgb(0x0b0e14),
    shadow: Color32::from_black_alpha(70),
    scene: Scene {
        sky: [rgb(0x080910), rgb(0x131422), rgb(0x271c32)],
        star_strength: 1.0,
        aurora_strength: 1.1,
        snow: rgb(0xfde68a),
        rim: rgba(0xfde68a, 70),
        snow_cap: rgba(0xfef3c7, 120),
        mountains: [
            (rgb(0x352b44), rgb(0x1b1626)),
            (rgb(0x231d30), rgb(0x120f1c)),
            (rgb(0x15121e), rgb(0x0b0912)),
        ],
        celestial: Celestial::Moon,
        mist: rgba(0x352b44, 60),
        trees: rgb(0x08070e),
    },
};

pub fn palette(mode: ThemeMode) -> &'static Palette {
    match mode {
        ThemeMode::Default => &DEFAULT,
        ThemeMode::Dark => &DARK,
        ThemeMode::Light => &LIGHT,
        ThemeMode::Glass => &GLASS,
    }
}

const RADIUS: u8 = 6;
const SMALL_TEXT: f32 = 12.0;
const BODY_TEXT: f32 = 13.5;

pub fn apply(ctx: &egui::Context, p: &Palette) {
    let (theme, mut v) = if p.dark {
        (Theme::Dark, egui::Visuals::dark())
    } else {
        (Theme::Light, egui::Visuals::light())
    };
    ctx.set_theme(theme);
    v.override_text_color = Some(p.text);
    v.panel_fill = p.bg;
    // Menus, dropdowns and tooltips (egui's popups) sit over the scenery like dialogs do.
    v.window_fill = dialog_fill(p);
    v.extreme_bg_color = if p.dark {
        p.bg.gamma_multiply(0.7)
    } else {
        rgb(0xffffff)
    };
    v.faint_bg_color = p.surface;
    v.hyperlink_color = p.accent;
    v.warn_fg_color = p.warn;
    v.error_fg_color = p.error;
    v.selection.bg_fill = p.accent_deep.gamma_multiply(0.45);
    v.selection.stroke = Stroke::new(1.0, p.accent);
    v.window_stroke = Stroke::new(1.0, p.surface_hover);

    let radius = CornerRadius::same(RADIUS);
    let w = &mut v.widgets;
    for (state, fill) in [
        (&mut w.inactive, p.surface),
        (&mut w.hovered, p.surface_hover),
        (&mut w.active, p.accent_deep.gamma_multiply(0.6)),
        (&mut w.open, p.surface_hover),
    ] {
        state.bg_fill = fill;
        state.weak_bg_fill = fill;
        state.corner_radius = radius;
    }
    w.noninteractive.bg_fill = p.surface;
    w.noninteractive.weak_bg_fill = p.surface;
    w.noninteractive.bg_stroke = Stroke::new(1.0, p.surface);
    w.noninteractive.corner_radius = radius;
    w.hovered.bg_stroke = Stroke::new(1.0, p.accent.gamma_multiply(0.6));

    ctx.set_visuals_of(theme, v);
    ctx.style_mut_of(theme, |style| {
        style.spacing.item_spacing = egui::vec2(8.0, 8.0);
        style.spacing.button_padding = egui::vec2(12.0, 6.0);
        // egui's small text (9 px) is too hard to read for notes and hints.
        if let Some(small) = style.text_styles.get_mut(&egui::TextStyle::Small) {
            small.size = SMALL_TEXT;
        }
        if let Some(body) = style.text_styles.get_mut(&egui::TextStyle::Body) {
            body.size = BODY_TEXT;
        }
    });
}

/// A dialog's (and a popup's) background. Glass's see-through surface reads poorly over the aurora once a
/// dialog's text sits on it (dialogs aren't blurred like the panes), so there it's the night's
/// own color, nearly solid; the other themes use their surface as it is.
pub fn dialog_fill(p: &Palette) -> Color32 {
    if p.glass {
        Color32::from_rgba_unmultiplied(0x0e, 0x1a, 0x2c, DIALOG_GLASS_ALPHA)
    } else {
        p.surface
    }
}

/// How solid Glass dialogs are (of 255).
const DIALOG_GLASS_ALPHA: u8 = 242;

/// Frosted-ice card: translucent so the scenery shows through, with a
/// faint edge and a soft drop shadow.
pub fn card(p: &Palette) -> egui::Frame {
    egui::Frame::new()
        .fill(p.card_fill)
        .stroke(Stroke::new(1.0, p.card_stroke))
        .corner_radius(CornerRadius::same(12))
        .inner_margin(16.0)
        .shadow(egui::Shadow {
            offset: [0, 6],
            blur: 18,
            spread: 0,
            color: p.shadow,
        })
}

/// Side navigation: frosted glass with a faint right edge.
pub fn nav_frame(p: &Palette) -> egui::Frame {
    egui::Frame::new().fill(p.nav_fill).inner_margin(12.0)
}

/// Solid strip for the update banner and notices.
pub fn strip(p: &Palette) -> egui::Frame {
    egui::Frame::new().fill(p.surface).inner_margin(8.0)
}
