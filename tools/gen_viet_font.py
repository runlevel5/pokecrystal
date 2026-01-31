#!/usr/bin/env python3
"""
Generate Vietnamese font PNG for Pokemon Crystal.

This creates a modified font.png with Vietnamese characters replacing
the uppercase A-Z and other unused slots, while keeping lowercase a-z,
digits, and essential punctuation.

IMPORTANT: Output must be pure black (#000000) and white (#FFFFFF) only!
The Game Boy can only handle 1bpp (2 color) fonts.
"""

from PIL import Image, ImageDraw, ImageFont
import os
import sys

# Vietnamese characters mapped to their tile positions (0-127, corresponding to $80-$FF)
# Position = slot - 0x80
VIET_CHAR_POSITIONS = {
    # Row 0: $80-$8F (positions 0-15)
    0: "ă",
    1: "ắ",
    2: "ằ",
    3: "ẳ",
    4: "ẵ",
    5: "ặ",
    6: "â",
    7: "ấ",
    8: "ầ",
    9: "ẩ",
    10: "ẫ",
    11: "ậ",
    12: "ê",
    13: "ế",
    14: "ề",
    15: "ể",
    # Row 1: $90-$9F (positions 16-31)
    16: "ễ",
    17: "ệ",
    18: "ô",
    19: "ố",
    20: "ồ",
    21: "ổ",
    22: "ỗ",
    23: "ộ",
    24: "ơ",
    25: "ớ",
    26: "ờ",
    27: "ở",
    # 28 = ":" (keep from original)
    29: "ỡ",
    30: "ợ",
    31: "ư",
    # Row 2: $A0-$AF (positions 32-47) - lowercase a-p, KEEP from original
    # Row 3: $B0-$BF (positions 48-63)
    # 48-57 = q-z (keep from original)
    58: "ứ",
    59: "ừ",
    60: "ử",
    61: "ữ",
    62: "ự",
    63: "á",
    # Row 4: $C0-$CF (positions 64-79)
    64: "à",
    65: "ả",
    66: "ã",
    67: "ạ",
    68: "è",
    69: "ẻ",
    70: "ẽ",
    71: "ẹ",
    72: "í",
    73: "ì",
    74: "ỉ",
    75: "ĩ",
    76: "ị",
    77: "ó",
    78: "ò",
    79: "ỏ",
    # Row 5: $D0-$DF (positions 80-95)
    80: "õ",
    81: "ọ",
    82: "ú",
    83: "ù",
    84: "ủ",
    85: "ũ",
    86: "ụ",
    87: "ý",
    88: "ỳ",
    89: "ỷ",
    90: "ỹ",
    91: "ỵ",
    92: "đ",
    # 93-95: keep from original (unused, unused, ←)
    # Row 6-7: $E0-$FF (positions 96-127) - keep from original
}

# Positions to keep from original font (don't overwrite)
KEEP_FROM_ORIGINAL = set(range(32, 58))  # a-z (positions 32-57)
KEEP_FROM_ORIGINAL.add(28)  # : at $9C
KEEP_FROM_ORIGINAL.update(range(93, 128))  # $DD-$FF: keep ←, ', symbols, digits


def create_viet_font(original_path, output_path, pixel_font_path=None):
    """
    Create Vietnamese font by modifying the original font.png.
    Output is pure black and white (1-bit).
    """
    # Load original font
    if not os.path.exists(original_path):
        print(f"Error: Original font not found at {original_path}")
        sys.exit(1)

    original = Image.open(original_path).convert("L")  # Grayscale
    width, height = original.size
    tile_size = 8
    cols = width // tile_size  # 16

    print(f"Original font: {width}x{height}, {cols} columns")

    # Create a copy to modify (keep as grayscale for drawing)
    img = original.copy()
    draw = ImageDraw.Draw(img)

    # Try to load a suitable font for Vietnamese
    font = None
    font_size = 8

    # Try custom pixel font first
    if pixel_font_path and os.path.exists(pixel_font_path):
        try:
            font = ImageFont.truetype(pixel_font_path, font_size)
            print(f"Using custom font: {pixel_font_path}")
        except Exception as e:
            print(f"Could not load custom font: {e}")

    # Fall back to system fonts
    if font is None:
        system_fonts = [
            # macOS
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
            # Linux
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            # Windows
            "C:\\Windows\\Fonts\\arial.ttf",
        ]
        for sf in system_fonts:
            if os.path.exists(sf):
                try:
                    font = ImageFont.truetype(sf, font_size)
                    print(f"Using system font: {sf}")
                    break
                except Exception:
                    continue

    if font is None:
        font = ImageFont.load_default()
        print("Using default font (may not support Vietnamese)")

    # Draw Vietnamese characters
    chars_drawn = 0
    for pos, char in VIET_CHAR_POSITIONS.items():
        if pos in KEEP_FROM_ORIGINAL:
            continue

        col = pos % cols
        row = pos // cols
        x = col * tile_size
        y = row * tile_size

        # Clear the tile (white background)
        draw.rectangle([x, y, x + tile_size - 1, y + tile_size - 1], fill=255)

        # Get text bounding box
        bbox = draw.textbbox((0, 0), char, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Center character in 8×8 cell
        text_x = x + (tile_size - text_width) // 2 - bbox[0]
        # Position text near top to leave room for base vowels with diacritics above
        text_y = y + 1 - bbox[1]

        # Draw character in black
        draw.text((text_x, text_y), char, fill=0, font=font)
        chars_drawn += 1

    print(f"Drew {chars_drawn} Vietnamese characters")

    # Convert to pure black and white (1-bit)
    # Threshold at 128: anything below is black, above is white
    img = img.point(lambda x: 0 if x < 128 else 255, mode="L")

    # Convert to 1-bit mode for smallest file size
    img_bw = img.convert("1")

    # Save as PNG (will be black and white)
    img_bw.save(output_path)
    print(f"Saved to {output_path}")

    # Verify color count
    colors = img_bw.getcolors()
    print(f"Colors in output: {len(colors)} (should be 2)")

    return img_bw


def print_charmap():
    """Print the charmap entries for Vietnamese characters."""
    print("\n; Vietnamese character mappings for charmap.asm")
    for pos in sorted(VIET_CHAR_POSITIONS.keys()):
        if pos in KEEP_FROM_ORIGINAL:
            continue
        char = VIET_CHAR_POSITIONS[pos]
        slot = 0x80 + pos
        print(f'\tcharmap "{char}",         ${slot:02x}')


if __name__ == "__main__":
    original = "gfx/font/font_original.png"
    output = sys.argv[1] if len(sys.argv) > 1 else "gfx/font/font.png"
    pixel_font = sys.argv[2] if len(sys.argv) > 2 else None

    create_viet_font(original, output, pixel_font)
