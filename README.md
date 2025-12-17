Python script to generate Paint by Numbers artwork from any input image. It:
Resizes the input image to a manageable size.
Quantizes it to a specified number of colors using Pillow's efficient median-cut algorithm.
Generates an outline image with black boundaries around color regions and centered numbers in each sufficiently large region of the same color.
Creates a color legend/key image mapping numbers to color swatches.
