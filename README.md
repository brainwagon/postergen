# PosterGen

PosterGen is a Python script for creating large bitmap images suitable for printing as posters. It combines text and images in a simple and aesthetically pleasing way.

## Usage

To use PosterGen, you first create an input file that defines the content and layout of your poster. Then, you run the script with the input file as an argument.

```bash
python postergen.py input.txt
```

The script will generate an image file (by default, `output.png`) based on the instructions in your input file. You can specify a different output file name using the `-o` flag:

```bash
python postergen.py input.txt -o my_poster.png
```

You can also override the size and margin settings from the command line:

```bash
python postergen.py input.txt --size 800x600 --margin 10%
```

## Input File Syntax

The input file is a plain text file where each line is one of the following:

1.  A global directive
2.  A line of text to be rendered
3.  The path to an image file
4.  A comment

### Comments

Lines beginning with a `#` are considered comments and are ignored.

### Global Directives

Global directives start with an `!` and affect the entire poster.

*   `!font <font_name>`: Sets the font for all subsequent text. This command can be used multiple times in the input file to change fonts for different parts of the poster. You can use the name of a font (e.g., `Arial`) or the path to a `.ttf` file (e.g., `TNG_Credits.ttf`). The default font is Arial.
*   `!size <width>x<height>`: Sets the size of the output image. The default is `1024x1536`.
*   `!margin <value>`: Sets the margin for the poster. The value can be a percentage (e.g., `5%`) or in pixels. The default is `5%`.
*   `!background_color <color>`: Sets the background color of the poster. You can use color names (e.g., `white`, `black`) or hex codes (e.g., `#DDDDDD`). The default is `white`.
*   `!background_image <path_to_image>`: Sets an image to be used as the background for the entire poster. The image is resized to the full dimensions of the poster, ignoring the original aspect ratio. This background is drawn first, and all other content, including the margin, will be placed on top of it.

**Example:**

```
!font TNG_Credits.ttf
!size 2000x3000
!margin 10%
!background_color #333333
```

### Text

To render text, simply add it to a new line in the input file. You can control the alignment, size, and color of the text using special keywords.

*   **Alignment:** `alignment=<value>`, where `<value>` can be `left`, `center`, or `right`. The default is `center`.
*   **Size:**
    *   `size=bigger`: Makes the text larger than the default size. Can be used multiple times (e.g., `size=bigger size=bigger`).
    *   `size=smaller`: Makes the text smaller than the default size. Can be used multiple times.
    *   `size=<value>`: Sets the font size in pixels (e.g., `size=48`) or as a percentage of the image height (e.g., `size=10%`).
*   **Color:** `color=<color>`: Sets the color of the text. You can use color names (e.g., `red`, `blue`) or hex codes (e.g., `#FF0000`). The default is `black`.

Keywords can be combined.

**Examples:**

```
This is centered text.
alignment=left This is left-justified text.
alignment=right size=bigger This is right-justified, larger text.
size=60 color=blue This text has a specific pixel size and is blue.
size=5% color=#00FF00 This text has a specific percentage size and is green.
```

An empty line will create a blank space, which is 25% of the height of a normal text line.

### Images

To include an image, add the path to the image file on a new line. You can control the size of the image using keywords.

*   `width=<value>`: Sets the width of the image in pixels or as a percentage of the image width. The aspect ratio will be maintained.
*   `height=<value>`: Sets the height of the image in pixels or as a percentage of the image height. The aspect ratio will be maintained.
*   `width=<value> height=<value>`: Sets both the width and height of the image. The aspect ratio may not be maintained.

**Examples:**

```
my_image.jpg
my_image.jpg width=50%
my_image.jpg height=300
my_image.jpg width=400 height=400
```

## Layout Algorithm

The script uses a sophisticated, multi-pass approach to calculate the layout of the poster, ensuring that all elements fit together in an aesthetically pleasing way.

1.  **Initial Height Calculation:** The script first determines the initial height of each element. Elements with explicit heights (e.g., `height=300`) have their heights fixed. The remaining vertical space is then distributed among the other elements.

2.  **Font Size Grouping:** Text lines are grouped based on their size modifiers (e.g., `bigger`, `smaller`, or the default). For each group, the script determines a unified font size by finding the widest line in that group and scaling it to fit within the poster's margins.

3.  **Final Height Calculation:** The script then calculates the final rendered height of each element, taking into account the actual font metrics of the text. This ensures that the layout is accurate, regardless of the font being used.

4.  **Whitespace Distribution:** Any extra vertical whitespace that results from scaling down the text is evenly distributed between the top and bottom margins of the poster, creating a clean and balanced look.

5.  **Rendering:** Finally, the script renders the poster from top to bottom, placing each element according to its calculated height and position.