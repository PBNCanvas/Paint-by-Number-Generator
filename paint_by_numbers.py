import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def dilate_cross(mask):
    """Simple cross-shaped morphological dilation (pure NumPy)."""
    new_mask = mask.copy()
    new_mask[1:, :] |= mask[:-1, :]
    new_mask[:-1, :] |= mask[1:, :]
    new_mask[:, 1:] |= mask[:, :-1]
    new_mask[:, :-1] |= mask[:, 1:]
    return new_mask

def main():
    parser = argparse.ArgumentParser(description='Paint by Numbers generator')
    parser.add_argument('input', help='Input image path')
    parser.add_argument('-o', '--output', default='outline.png', help='Output outline image (default: outline.png)')
    parser.add_argument('-k', '--key', default='color_key.png', help='Output color key (default: color_key.png)')
    parser.add_argument('-n', '--ncolors', type=int, default=25, help='Number of colors (default: 25)')
    parser.add_argument('-s', '--size', type=int, default=400, help='Max side length after resize (0=disable, default: 400)')
    parser.add_argument('-a', '--min-area', type=int, default=100, help='Min region area for number (default: 100)')
    parser.add_argument('-d', '--dilation', type=int, default=2, help='Boundary dilation iterations (default: 2)')
    args = parser.parse_args()

    # Load and preprocess image
    orig = Image.open(args.input).convert('RGB')
    h_orig, w_orig = orig.size[1], orig.size[0]
    ratio = 1.0
    if args.size > 0 and max(w_orig, h_orig) > args.size:
        ratio = args.size / max(w_orig, h_orig)
    new_w = int(w_orig * ratio)
    new_h = int(h_orig * ratio)
    img = orig.resize((new_w, new_h), Image.Resampling.LANCZOS)
    np_img = np.array(img, dtype=np.uint8)

    # Quantize
    pal_img = img.quantize(colors=args.ncolors, method=2).convert('P')
    labels = np.array(pal_img, dtype=np.uint8)
    h, w = labels.shape

    # Get palette colors (RGB tuples)
    pal = pal_img.getpalette()[:args.ncolors * 3]
    num_colors = min(args.ncolors, len(pal) // 3)
    colors = [(pal[i*3], pal[i*3+1], pal[i*3+2]) for i in range(num_colors)]

    # Compute edge mask
    edge_mask = np.zeros((h, w), dtype=bool)
    # Horizontal edges
    horiz_diff = np.abs(labels[:-1, :] - labels[1:, :]) > 0
    edge_mask[:-1, :] |= horiz_diff
    edge_mask[1:, :] |= horiz_diff
    # Vertical edges
    vert_diff = np.abs(labels[:, :-1] - labels[:, 1:]) > 0
    edge_mask[:, :-1] |= vert_diff
    edge_mask[:, 1:] |= vert_diff

    # Dilate boundaries for thickness
    boundary = edge_mask.copy()
    for _ in range(args.dilation):
        boundary = dilate_cross(boundary)

    # Create outline image (white bg, black boundaries)
    outline_np = np.full((h, w, 3), 255, dtype=np.uint8)
    outline_np[boundary] = 0
    outline_img = Image.fromarray(outline_np)
    draw = ImageDraw.Draw(outline_img)

    # Prepare rows/cols for center of mass
    rows = np.tile(np.arange(h)[:, np.newaxis], (1, w)).astype(float)
    cols = np.tile(np.arange(w)[np.newaxis, :], (h, 1)).astype(float)

    # Place numbers in large regions per color
    fontsize = max(12, min(36, h // 20))
    font_paths = ['arial.ttf', '/System/Library/Fonts/Arial.ttf', 'C:/Windows/Fonts/arial.ttf']
    font = ImageFont.load_default()
    for fpath in font_paths:
        try:
            font = ImageFont.truetype(fpath, fontsize)
            break
        except OSError:
            continue

    for k in range(num_colors):
        mask = (labels == k)
        total_area = np.sum(mask)
        if total_area < args.min_area:
            continue
        cy = np.sum(rows * mask) / total_area
        cx = np.sum(cols * mask) / total_area
        text = str(k + 1)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        draw.text((cx - text_width / 2, cy - text_height / 2), text, fill=(0, 0, 0), font=font)

    # Save outline
    outline_img.save(args.output)
    print(f"Outline saved: {args.output}")

    # Create color key legend
    legend_cols = 5
    legend_rows = (num_colors + legend_cols - 1) // legend_cols
    legend_w = legend_cols * 80
    legend_h = legend_rows * 50
    legend_img = Image.new('RGB', (legend_w, legend_h), 'white')
    draw = ImageDraw.Draw(legend_img)
    cell_w, cell_h = 40, 40
    text_offset_x, text_offset_y = 50, 8
    for i in range(num_colors):
        row = i // legend_cols
        col = i % legend_cols
        x = col * 80 + 10
        y = row * 50 + 5
        draw.rectangle((x, y, x + cell_w, y + cell_h), fill=colors[i])
        draw.text((x + text_offset_x, y + text_offset_y), str(i + 1), fill=(0, 0, 0), font=font)
    legend_img.save(args.key)
    print(f"Color key saved: {args.key}")

if __name__ == '__main__':
    main()