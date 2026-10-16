package com.arcticlauncher.client.style;

/**
 * A menu style: the palette for Arctic screens and restyled vanilla
 * widgets. {@link #VANILLA} keeps Minecraft's own menus.
 */
public final class Style {
	public final String id;
	public final String name;
	public final String description;
	/** Replace the title screen and restyle vanilla widgets. */
	public final boolean restyles;

	public final int accent;
	public final int onAccent;
	public final int skyTop;
	public final int skyBottom;
	public final int aurora;
	public final int mountainsBack;
	public final int mountainsFront;
	public final int panel;
	public final int border;
	public final int button;
	public final int buttonHover;
	public final int buttonOff;
	public final int field;
	public final int text;
	public final int muted;
	public final int hud;

	private Style(Builder b) {
		id = b.id;
		name = b.name;
		description = b.description;
		restyles = b.restyles;
		accent = b.accent;
		onAccent = b.onAccent;
		skyTop = b.skyTop;
		skyBottom = b.skyBottom;
		aurora = b.aurora;
		mountainsBack = b.mountainsBack;
		mountainsFront = b.mountainsFront;
		panel = b.panel;
		border = b.border;
		button = b.button;
		buttonHover = b.buttonHover;
		buttonOff = b.buttonOff;
		field = b.field;
		text = b.text;
		muted = b.muted;
		hud = b.hud;
	}

	public static final Style ARCTIC = new Builder("duckling", "Duckling", "Warm golden yellow with duckling accents.")
			.accent(0xFFFBBF24, 0xFF3D2800)
			.sky(0xFF1E170A, 0xFF382910, 0x60FBBF24)
			.mountains(0xFF4A3716, 0xFF241A0A)
			.surfaces(0xE020160A, 0x40FBBF24, 0xB03B2A12, 0xD85A411B, 0x80261B0B, 0xC01A1207)
			.ink(0xFFFFFBEB, 0xFFD4A359, 0x901A1207)
			.build();

	public static final Style AURORA = new Builder("aurora", "Aurora", "Violet sky with northern-light greens.")
			.accent(0xFF86EFAC, 0xFF0B2A18)
			.sky(0xFF0B0A1C, 0xFF231A45, 0x5886EFAC)
			.mountains(0xFF2A2350, 0xFF151130)
			.surfaces(0xE0120F26, 0x4086EFAC, 0xB0221C42, 0xD8322963, 0x8016132A, 0xC00E0B20)
			.ink(0xFFF1EEFF, 0xFFA69CC8, 0x900E0B20)
			.build();

	public static final Style CLASSIC = new Builder("classic", "Classic", "Plain black and white, no colors.")
			.accent(0xFFE8E8E8, 0xFF000000)
			.sky(0xFF000000, 0xFF121212, 0x00FFFFFF)
			.mountains(0xFF1C1C1C, 0xFF0A0A0A)
			.surfaces(0xE8050505, 0x40FFFFFF, 0xB0161616, 0xD82A2A2A, 0x80101010, 0xC0000000)
			.ink(0xFFF2F2F2, 0xFF9A9A9A, 0x90000000)
			.build();

	public static final Style VANILLA = new Builder("vanilla", "Vanilla", "Minecraft's own menus, plus the Duckling HUD.")
			.restyles(false)
			.accent(0xFFFFFFFF, 0xFF202020)
			.sky(0xFF101010, 0xFF2A2A2A, 0x00FFFFFF)
			.mountains(0xFF303030, 0xFF1C1C1C)
			.surfaces(0xE0181818, 0x40FFFFFF, 0xB0303030, 0xD8484848, 0x80202020, 0xC0101010)
			.ink(0xFFFFFFFF, 0xFFA0A0A0, 0x90000000)
			.build();

	public static final Style[] ALL = {ARCTIC, AURORA, CLASSIC, VANILLA};

	public static Style byId(String id) {
		for (Style s : ALL) {
			if (s.id.equals(id) || ("arctic".equals(id) && "duckling".equals(s.id))) {
				return s;
			}
		}
		return ARCTIC;
	}

	private static final class Builder {
		final String id;
		final String name;
		final String description;
		boolean restyles = true;
		int accent;
		int onAccent;
		int skyTop;
		int skyBottom;
		int aurora;
		int mountainsBack;
		int mountainsFront;
		int panel;
		int border;
		int button;
		int buttonHover;
		int buttonOff;
		int field;
		int text;
		int muted;
		int hud;

		Builder(String id, String name, String description) {
			this.id = id;
			this.name = name;
			this.description = description;
		}

		Builder restyles(boolean on) {
			restyles = on;
			return this;
		}

		Builder accent(int accent, int onAccent) {
			this.accent = accent;
			this.onAccent = onAccent;
			return this;
		}

		Builder sky(int top, int bottom, int aurora) {
			skyTop = top;
			skyBottom = bottom;
			this.aurora = aurora;
			return this;
		}

		Builder mountains(int back, int front) {
			mountainsBack = back;
			mountainsFront = front;
			return this;
		}

		Builder surfaces(int panel, int border, int button, int buttonHover, int buttonOff, int field) {
			this.panel = panel;
			this.border = border;
			this.button = button;
			this.buttonHover = buttonHover;
			this.buttonOff = buttonOff;
			this.field = field;
			return this;
		}

		Builder ink(int text, int muted, int hud) {
			this.text = text;
			this.muted = muted;
			this.hud = hud;
			return this;
		}

		Style build() {
			return new Style(this);
		}
	}
}
