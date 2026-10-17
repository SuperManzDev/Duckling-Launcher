//! Duckling's beloved community cause: SITS (Student Information Technology Services).
//!
//! Refurbishing old tech, educating students, and donating computers to
//! families and children in need from Canton room CV 26.
//!
//! "WE LOVE SITS" in the sidebar, About, and Play Together tabs.
//! Settings → "Show supporter mentions" can hide it if desired.

use eframe::egui::{
    self, Align2, CornerRadius, CursorIcon, FontId, Id, Modal, Rect, RichText, Sense, Stroke,
    StrokeKind, vec2,
};

use crate::app::DucklingApp;
use crate::art::icons::Icon;
use crate::art::sits;
use crate::theme;
use crate::toasts::Kind;
use crate::widgets;

pub const NAME: &str = "WE LOVE SITS";
pub const ORG_NAME: &str = "Student Information Technology Services";
pub const URL: &str = "https://sitservices.org/";
pub const DONATED_COUNT: &str = "0 1 2 6";
pub const PITCH: &str =
    "Refurbishing hardware & donating PCs to children and families in need (Canton CV 26).";

impl DucklingApp {
    /// Sidebar, above the account switcher: SITS logo, "WE LOVE SITS", and Easter egg duck.
    pub(crate) fn sponsor_sidebar(&mut self, ui: &mut egui::Ui) {
        if !self.settings.show_sponsor {
            return;
        }
        let p = self.palette();
        let width = ui.available_width();
        let (rect, response) = ui.allocate_exact_size(vec2(width, 38.0), Sense::click());
        let hovered = response.hovered();

        if hovered {
            ui.painter().rect_filled(
                rect,
                CornerRadius::same(10),
                p.accent_deep.gamma_multiply(0.22),
            );
            ui.painter().rect_stroke(
                rect,
                CornerRadius::same(10),
                Stroke::new(1.0, sits::BLUE.gamma_multiply(0.4)),
                StrokeKind::Inside,
            );
        }

        // Render SITS logo on the left
        let logo_rect = Rect::from_center_size(
            egui::pos2(rect.left() + 26.0, rect.center().y),
            vec2(38.0, 18.0),
        );
        sits::logo(ui.ctx(), ui.painter(), logo_rect);

        // Name and subtitle
        let title_color = if hovered { sits::DUCK_GOLD } else { p.text };
        ui.painter().text(
            egui::pos2(rect.left() + 52.0, rect.center().y - 7.0),
            Align2::LEFT_CENTER,
            "WE LOVE SITS",
            FontId::proportional(12.0),
            title_color,
        );
        ui.painter().text(
            egui::pos2(rect.left() + 52.0, rect.center().y + 7.5),
            Align2::LEFT_CENTER,
            "sitservices.org • CV 26",
            FontId::proportional(10.0),
            p.muted,
        );

        // Easter egg duckling icon on the right
        let duck_rect = Rect::from_center_size(
            egui::pos2(rect.right() - 16.0, rect.center().y),
            vec2(18.0, 18.0),
        );
        let duck_response = ui.interact(duck_rect, Id::new("sits_sidebar_duck"), Sense::click());
        let duck_hovered = duck_response.hovered();
        ui.painter().text(
            duck_rect.center(),
            Align2::CENTER_CENTER,
            "🦆",
            FontId::proportional(if duck_hovered { 15.0 } else { 13.0 }),
            if duck_hovered {
                sits::DUCK_GOLD
            } else {
                p.muted
            },
        );

        if duck_response
            .on_hover_cursor(CursorIcon::PointingHand)
            .on_hover_text("🦆 Click to open SITS Story & Duck Easter Egg!")
            .clicked()
        {
            self.sits_easter_egg = true;
            return;
        }

        let tooltip = format!(
            "💛 Student Information Technology Services (SITS)\n\
             Computers Donated: {DONATED_COUNT} 💻🦆\n\
             Drop-off: Canton room CV 26 (6:30 AM – 3:00 PM)\n\n\
             • Left click: visit {URL}\n\
             • Right click or click 🦆: open SITS Story & Easter Egg!"
        );

        let response = response
            .on_hover_cursor(CursorIcon::PointingHand)
            .on_hover_text(tooltip);

        if response.clicked() {
            ui.ctx().open_url(egui::OpenUrl::new_tab(URL));
        } else if response.secondary_clicked() {
            self.sits_easter_egg = true;
        }
    }

    /// About tab: "WE LOVE SITS" with logo, link, and Easter Egg button.
    pub(crate) fn sponsor_credit(&mut self, ui: &mut egui::Ui) {
        if !self.settings.show_sponsor {
            return;
        }
        let p = self.palette();
        let row = vec2(ui.available_width(), 38.0);
        ui.allocate_ui_with_layout(
            row,
            egui::Layout::left_to_right(egui::Align::Center),
            |ui| {
                ui.label(RichText::new("Proudly supporting:").color(p.muted));
                let (mark, _) = ui.allocate_exact_size(vec2(44.0, 20.0), Sense::hover());
                sits::logo(ui.ctx(), ui.painter(), mark);
                ui.label(RichText::new(NAME).strong().color(sits::DUCK_GOLD));
                if widgets::button(ui, p, Some(Icon::External), "sitservices.org", false)
                    .on_hover_text(URL)
                    .clicked()
                {
                    ui.ctx().open_url(egui::OpenUrl::new_tab(URL));
                }
                if widgets::button(ui, p, None, "🦆 SITS Story & Easter Egg", false)
                    .on_hover_text("Read the SITS refurbishment story and quack!")
                    .clicked()
                {
                    self.sits_easter_egg = true;
                }
            },
        );
    }

    /// Playing together: a card celebrating SITS hardware refurbishing.
    pub(crate) fn sponsor_card(&mut self, ui: &mut egui::Ui) {
        if !self.settings.show_sponsor {
            return;
        }
        let p = self.palette();
        theme::card(p).show(ui, |ui| {
            ui.set_width(ui.available_width());
            crate::widgets::row(ui, |ui| {
                let (mark, _) = ui.allocate_exact_size(vec2(72.0, 32.0), Sense::hover());
                sits::logo(ui.ctx(), ui.painter(), mark);
                ui.add_space(8.0);
                ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                    if widgets::button(ui, p, None, "🦆 SITS Story", false)
                        .on_hover_text("Open SITS Story & Easter Egg")
                        .clicked()
                    {
                        self.sits_easter_egg = true;
                    }
                    if widgets::button(ui, p, Some(Icon::External), "sitservices.org", false)
                        .on_hover_text(URL)
                        .clicked()
                    {
                        ui.ctx().open_url(egui::OpenUrl::new_tab(URL));
                    }
                    ui.add_space(12.0);
                    ui.with_layout(egui::Layout::top_down(egui::Align::Min), |ui| {
                        ui.horizontal(|ui| {
                            ui.label(RichText::new(NAME).size(15.0).strong().color(p.text));
                            ui.label(
                                RichText::new(format!("• {DONATED_COUNT} Computers Donated 💻"))
                                    .small()
                                    .color(sits::BLUE),
                            );
                        });
                        ui.add(
                            egui::Label::new(
                                RichText::new(format!(
                                    "Student Information Technology Services: taking in decommissioned \
                                     tech in Canton room CV 26, upgrading it, and donating to families \
                                     without computers. {PITCH}"
                                ))
                                .color(p.muted),
                            )
                            .wrap(),
                        );
                    });
                });
            });
        });
    }

    /// The interactive SITS Easter Egg & Story Modal dialog.
    pub(crate) fn sits_easter_egg_dialog(&mut self, ctx: &egui::Context) {
        if !self.sits_easter_egg {
            return;
        }
        let p = self.palette();
        let modal = Modal::new(Id::new("sits_easter_egg_dialog"))
            .frame(super::dialogs::dialog_frame(p).inner_margin(24.0))
            .show(ctx, |ui| {
                ui.set_width(520.0);

                // Top banner: Logo and Duckling header
                ui.vertical_centered(|ui| {
                    let (logo_rect, _) = ui.allocate_exact_size(vec2(160.0, 72.0), Sense::hover());
                    sits::logo(ui.ctx(), ui.painter(), logo_rect);
                    ui.add_space(4.0);
                    ui.label(
                        RichText::new("🦆 WE LOVE SITS 💻")
                            .size(24.0)
                            .strong()
                            .color(sits::DUCK_GOLD),
                    );
                    ui.label(
                        RichText::new(ORG_NAME)
                            .size(15.0)
                            .strong()
                            .color(p.text),
                    );
                });

                ui.add_space(10.0);

                // Counter Box
                let counter_frame = egui::Frame::new()
                    .fill(p.surface)
                    .stroke(Stroke::new(1.5, sits::BLUE))
                    .corner_radius(CornerRadius::same(12))
                    .inner_margin(12.0);
                counter_frame.show(ui, |ui| {
                    ui.vertical_centered(|ui| {
                        ui.label(
                            RichText::new("COMPUTERS DONATED TO DATE")
                                .size(11.0)
                                .color(p.muted),
                        );
                        ui.label(
                            RichText::new(DONATED_COUNT)
                                .size(28.0)
                                .strong()
                                .monospace()
                                .color(sits::BLUE),
                        );
                        ui.label(
                            RichText::new(
                                "Bridging the digital divide one machine at a time — Canton Room CV 26",
                            )
                            .size(12.0)
                            .color(p.text),
                        );
                    });
                });

                ui.add_space(12.0);

                egui::ScrollArea::vertical()
                    .max_height(260.0)
                    .show(ui, |ui| {
                        // Section 1: What SITS Does
                        ui.label(
                            RichText::new("What Does the SITS Team Do?")
                                .size(15.0)
                                .strong()
                                .color(sits::PURPLE),
                        );
                        ui.label(
                            RichText::new(
                                "• We take in and refurbish old hardware (guided by Mr. Obsniuk and student leaders)\n\
                                 • We educate our consumers and student technicians\n\
                                 • We donate our refurbished tech to households without computers\n\n\
                                 Once donations are received, student volunteers handle reconditioning from beginning \
                                 to end. All equipment is cleaned, tested, upgraded, and installed with open-source \
                                 operating systems and custom educational software packages.",
                            )
                            .color(p.text),
                        );

                        ui.add_space(10.0);

                        // Section 2: Donate & Drop-Off Info
                        ui.label(
                            RichText::new("Drop-Off & Contact Details")
                                .size(15.0)
                                .strong()
                                .color(sits::PINK),
                        );
                        ui.label(
                            RichText::new(
                                "Got unused computers, components, or peripherals? Drop them off at:\n\
                                 📍 Canton room CV 26 (Donations accepted 6:30 AM to 3:00 PM)\n\
                                 📞 Phone: 734-392-8713\n\
                                 ✉️ Email: studentinfotechservices@gmail.com\n\
                                 No donation is too small!",
                            )
                            .color(p.text),
                        );

                        ui.add_space(10.0);

                        // Section 3: Quack Easter Egg
                        ui.label(
                            RichText::new("Duckling Launcher Charity Partnership 🦆")
                                .size(15.0)
                                .strong()
                                .color(sits::DUCK_GOLD),
                        );
                        ui.label(
                            RichText::new(
                                "Every quack brings good vibes and clean open-source computing to kids in need. \
                                 Click the quack button below to cheer on the SITS tech crew!",
                            )
                            .color(p.muted),
                        );
                    });

                ui.add_space(12.0);

                // Quack Button & Action Buttons
                ui.horizontal(|ui| {
                    let quack_label = if self.sits_quacks == 0 {
                        "🦆 Quack for SITS!".to_string()
                    } else {
                        format!("🦆 Quack for SITS! ({})", self.sits_quacks)
                    };

                    if widgets::button(ui, p, None, &quack_label, true).clicked() {
                        self.sits_quacks += 1;
                        let quack_msgs = [
                            "🦆 *QUACK!* SITS refurbished computer #0126 is flying high!",
                            "🦆 *QUACK!* A student in Canton just got their first PC!",
                            "🦆 *QUACK!* Open-source educational software deployed with love!",
                            "🦆 *QUACK!* Thank you for supporting Student Information Technology Services!",
                            "🦆 *QUACK!* Mr. Obsniuk and the student techs say thanks!",
                        ];
                        let msg = quack_msgs[(self.sits_quacks as usize) % quack_msgs.len()];
                        self.toasts.push(Kind::Success, "🦆 SITS Quack!", msg);
                    }

                    if widgets::button(ui, p, Some(Icon::External), "Visit sitservices.org", false)
                        .on_hover_text(URL)
                        .clicked()
                    {
                        ui.ctx().open_url(egui::OpenUrl::new_tab(URL));
                    }

                    ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                        if widgets::button(ui, p, None, "Close", false).clicked() {
                            self.sits_easter_egg = false;
                        }
                    });
                });

                ui.add_space(6.0);
                ui.vertical_centered(|ui| {
                    ui.label(
                        RichText::new("© 2026 Student Information Technology Services (SITS). All rights reserved.")
                            .small()
                            .color(p.muted),
                    );
                });
            });

        if modal.should_close() {
            self.sits_easter_egg = false;
        }
    }
}
