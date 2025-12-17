Python script to generate Paint by Numbers artwork from any input image. It:

Resizes the input image to a manageable size.
Quantizes it to a specified number of colors using Pillow's efficient median-cut algorithm.
Generates an outline image with black boundaries around color regions and centered numbers in each sufficiently large region of the same color.
Creates a color legend/key image mapping numbers to color swatches.
Dependencies
Install with:

pip install pillow numpy
No other dependencies!

Usage
python paint_by_numbers.py input.jpg -o outline.png -k color_key.png -n 25 -s 400 -a 100
input: Path to input image (JPG, PNG, etc.).
-o/--output: Output path for the outline/numbers image (default: outline.png).
-k/--key: Output path for the color key (default: color_key.png).
-n/--ncolors: Number of colors (default: 25).
-s/--size: Max side length for resize (default: 400; use 0 to disable resize).
-a/--min-area: Min pixels per region for placing a number (default: 100).
-d/--dilation: Boundary thickness iterations (default: 2).
Example Output
Run on a photo: Gets a clean numbered outline ready for printing/coloring.
Adjust -n for more/fewer colors (10-50 works well).
-s 600 for larger canvases.
Numbers skip small regions; boundaries are smooth/thick.
Test with any image—it handles photos, drawings, etc. Tweak params as needed!
Demo: https://pbncanvas.com/generator
