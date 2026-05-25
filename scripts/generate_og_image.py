from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

PUBLIC = Path(__file__).resolve().parent.parent / "public"
FONT_DIR = "C:/Windows/Fonts"
W, H = 1200, 630

# Colors
BG = "#0f172a"  # slate-900
CARD = "#1e293b"  # slate-800
GREEN = "#22c55e"  # green-500
GREEN_LIGHT = "#bbf7d0"  # green-200
WHITE = "#ffffff"
MUTED = "#94a3b8"  # slate-400

# AQI band colors
BANDS = ["#50f0e6", "#50ccaa", "#f0e641", "#ff5050", "#960032", "#7d2181"]
BAND_W = 160

# Load fonts
arial = ImageFont.truetype(str(Path(FONT_DIR) / "arial.ttf"), 64)
arial_bold = ImageFont.truetype(str(Path(FONT_DIR) / "arialbd.ttf"), 72)
inter = ImageFont.truetype(str(Path(FONT_DIR) / "arial.ttf"), 26)
inter_small = ImageFont.truetype(str(Path(FONT_DIR) / "arial.ttf"), 22)

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

# AQI bands at bottom
band_y = H - 50
band_h = 16
total_band_w = len(BANDS) * BAND_W
band_start_x = (W - total_band_w) // 2
for i, c in enumerate(BANDS):
    x = band_start_x + i * BAND_W
    draw.rectangle([x, band_y, x + BAND_W, band_y + band_h], fill=c)

# Labels under bands
labels = ["Good", "Fair", "Moderate", "Poor", "Very Poor", "Extremely Poor"]
for i, (c, label) in enumerate(zip(BANDS, labels)):
    x = band_start_x + i * BAND_W + BAND_W // 2
    draw.text((x, band_y + band_h + 6), label, fill=MUTED, font=inter_small, anchor="mt")

# Title
draw.text((W // 2, 140), "Air Quality Ireland", fill=WHITE, font=arial_bold, anchor="mt")

# Subtitle
draw.text((W // 2, 230), "Live AQI, PM2.5, PM10, NO₂, O₃, SO₂", fill=GREEN_LIGHT, font=arial, anchor="mt")

# Description
desc = "Real-time air quality monitoring from 72 stations across Ireland"
draw.text((W // 2, 320), desc, fill=MUTED, font=inter, anchor="mt")

# Tagline
tag = "airqmon.code7dummy.workers.dev"
draw.text((W // 2, 380), tag, fill=GREEN, font=inter, anchor="mt")

# Decorative line
line_y = 430
draw.rectangle([(W // 2 - 80, line_y), (W // 2 + 80, line_y + 2)], fill=GREEN)

# Footer
footer = "Powered by EEA Air Quality Data — Updated every 6 hours"
draw.text((W // 2, 490), footer, fill=MUTED, font=inter_small, anchor="mt")

PUBLIC.mkdir(parents=True, exist_ok=True)
path = PUBLIC / "og-image.png"
img.save(str(path), "PNG")
print(f"OG image saved: {path} ({img.size[0]}x{img.size[1]})")
