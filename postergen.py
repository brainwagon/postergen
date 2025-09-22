import argparse
import os
import glob
import subprocess
from PIL import Image, ImageDraw, ImageFont

def get_font_map():
    font_map = {}
    font_paths = ['./']
    if os.name == 'posix':
        font_paths.extend([
            '/usr/share/fonts/',
            '/usr/local/share/fonts/',
            os.path.expanduser('~/.fonts'),
        ])

    for path in font_paths:
        for font_file in glob.glob(os.path.join(path, '**/*.ttf'), recursive=True):
            try:
                font = ImageFont.truetype(font_file)
                font_map[f'{font.getname()[0]} {font.getname()[1]}'] = font_file
            except OSError:
                pass
        for font_file in glob.glob(os.path.join(path, '**/*.otf'), recursive=True):
            try:
                font = ImageFont.truetype(font_file)
                font_map[f'{font.getname()[0]} {font.getname()[1]}'] = font_file
            except OSError:
                pass
        for font_file in glob.glob(os.path.join(path, '**/*.ttc'), recursive=True):
            try:
                # For TTC files, we need to iterate through the fonts in the collection
                font_collection = ImageFont.truetype(font_file)
                for i in range(100): # Try up to 100 fonts in a collection
                    try:
                        font = ImageFont.truetype(font_file, index=i)
                        font_map[f'{font.getname()[0]} {font.getname()[1]}'] = f"{font_file}:{i}"
                    except OSError:
                        break
            except OSError:
                pass
    return font_map

def list_fonts(common_only=False):
    font_map = get_font_map()
    common_fonts = [
        'Arial Regular',
        'Arial Bold',
        'Arial Italic',
        'Arial Bold Italic',
        'Arial Black Regular',
        'Comic Sans MS Regular',
        'Comic Sans MS Bold',
        'Courier New Regular',
        'Courier New Bold',
        'Courier New Italic',
        'Courier New Bold Italic',
        'Georgia Regular',
        'Georgia Bold',
        'Georgia Italic',
        'Georgia Bold Italic',
        'Impact Regular',
        'Times New Roman Regular',
        'Times New Roman Bold',
        'Times New Roman Italic',
        'Times New Roman Bold Italic',
        'Trebuchet MS Regular',
        'Trebuchet MS Bold',
        'Trebuchet MS Italic',
        'Trebuchet MS Bold Italic',
        'Verdana Regular',
        'Verdana Bold',
        'Verdana Italic',
        'Verdana Bold Italic',
        'Helvetica Regular',
        'Helvetica Bold',
        'Helvetica Italic',
        'Helvetica Bold Italic',
        'Times Regular',
        'Times Bold',
        'Times Italic',
        'Times Bold Italic',
        'Garamond Regular',
        'Garamond Bold',
        'Garamond Italic',
        'Garamond Bold Italic',
        'Futura Regular',
        'Futura Bold',
        'Futura Italic',
        'Futura Bold Italic',
        'Bodoni Regular',
        'Bodoni Bold',
        'Bodoni Italic',
        'Bodoni Bold Italic',
        'Rockwell Regular',
        'Rockwell Bold',
        'Rockwell Italic',
        'Rockwell Bold Italic',
        'Franklin Gothic Regular',
        'Franklin Gothic Bold',
        'Franklin Gothic Italic',
        'Franklin Gothic Bold Italic',
        'Myriad Regular',
        'Myriad Bold',
        'Myriad Italic',
        'Myriad Bold Italic',
        'Minion Regular',
        'Minion Bold',
        'Minion Italic',
        'Minion Bold Italic',
        'Lucida Grande Regular',
        'Lucida Grande Bold',
        'Lucida Grande Italic',
        'Lucida Grande Bold Italic',
        'Gill Sans Regular',
        'Gill Sans Bold',
        'Gill Sans Italic',
        'Gill Sans Bold Italic',
    ]

    for name, path in sorted(font_map.items()):
        if common_only:
            if name in common_fonts:
                print(f'{name} ({os.path.basename(path)})')
        else:
            print(f'{name} ({os.path.basename(path)})')


class Poster:
    def __init__(self):
        self.elements = []
        self.width = 1024
        self.height = 1536
        self.margin = 0.05
        self.font = 'Arial'
        self.background_color = 'white'
        self.background_image = None

    def __repr__(self):
        return f"Poster(width={self.width}, height={self.height}, margin={self.margin}, font='{self.font}', background_color='{self.background_color}', background_image='{self.background_image}', elements={self.elements})"

class TextLine:
    def __init__(self, text, justification='center', size_modifier=0, size=None, color='black', font=None):
        self.text = text
        self.justification = justification
        self.size_modifier = size_modifier
        self.size = size
        self.height = 0
        self.color = color
        self.font = font

    def __repr__(self):
        return f"TextLine(text='{self.text}', justification='{self.justification}', size_modifier={self.size_modifier}, size={self.size}, height={self.height}, color='{self.color}', font='{self.font}')"

class ImageElement:
    def __init__(self, path, width=None, height=None):
        self.path = path
        self.width = width
        self.height = height

    def __repr__(self):
        return f"ImageElement(path='{self.path}', width={self.width}, height={self.height})"

class BlankLine:
    def __init__(self):
        self.height = 0

    def __repr__(self):
        return f"BlankLine(height={self.height})"



def parse_line(line, poster):
    line = line.strip()
    if not line:
        return BlankLine()
    if line.startswith('#'):
        return None

    parts = line.split()
    text_parts = []
    justification = 'center'
    size_modifier = 0
    size = None
    width = None
    height = None
    color = 'black'

    is_image = any('.jpg' in p or '.png' in p for p in parts)

    for part in parts:
        if part.startswith('alignment='):
            justification = part.split('=')[1]
        elif part.startswith('size='):
            size_value = part.split('=')[1]
            if size_value == 'bigger':
                size_modifier += 1
            elif size_value == 'smaller':
                size_modifier -= 1
            else:
                size = size_value
        elif part.startswith('width='):
            width = part.split('=')[1]
        elif part.startswith('height='):
            height = part.split('=')[1]
        elif part.startswith('color='):
            color = part.split('=')[1]
        else:
            text_parts.append(part)

    if is_image:
        if size and not height:
            height = size
        return ImageElement(" ".join(text_parts), width=width, height=height)
    else:
        return TextLine(" ".join(text_parts), justification=justification, size_modifier=size_modifier, size=size, color=color, font=poster.font)


def render_poster(poster, output_filename):
    if poster.background_image:
        image = Image.open(poster.background_image)
        image = image.resize((poster.width, poster.height))
        image = image.convert('RGB')
    else:
        image = Image.new('RGB', (poster.width, poster.height), poster.background_color)
    draw = ImageDraw.Draw(image)
    
    margin_x = int(poster.width * poster.margin)
    margin_y = int(poster.height * poster.margin)
    active_width = poster.width - 2 * margin_x
    active_height = poster.height - 2 * margin_y

    # Determine initial heights for all elements
    explicit_height_elements = []
    implicit_height_elements = []
    total_explicit_height = 0

    for element in poster.elements:
        if isinstance(element, TextLine):
            if element.size:
                if element.size.endswith('%'):
                    element.height = int(active_height * (float(element.size[:-1]) / 100))
                else:
                    element.height = int(element.size)
                total_explicit_height += element.height
                explicit_height_elements.append(element)
            else:
                implicit_height_elements.append(element)
        elif isinstance(element, ImageElement) and element.height:
            if str(element.height).endswith('%'):
                element.height = int(active_height * (float(str(element.height)[:-1]) / 100))
            else:
                element.height = int(element.height)
            total_explicit_height += element.height
            explicit_height_elements.append(element)
        else:
            implicit_height_elements.append(element)

    remaining_height = active_height - total_explicit_height
    if implicit_height_elements:
        total_implicit_units = 0
        for element in implicit_height_elements:
            if isinstance(element, BlankLine):
                total_implicit_units += 0.25
            else:
                total_implicit_units += 1
        
        if total_implicit_units > 0:
            unit_height = remaining_height / total_implicit_units
            for element in implicit_height_elements:
                if isinstance(element, BlankLine):
                    element.height = unit_height * 0.25
                elif isinstance(element, TextLine):
                    element.height = unit_height * (1.2 ** element.size_modifier)
                else:
                    element.height = unit_height

    # Group text lines by size_modifier and font
    text_groups = {}
    for element in poster.elements:
        if isinstance(element, TextLine):
            key = (element.size_modifier, element.font)
            if key not in text_groups:
                text_groups[key] = []
            text_groups[key].append(element)

    # Calculate font size for each group
    group_font_sizes = {}
    for key, group in text_groups.items():
        min_font_size = 1000
        for element in group:
            try:
                font_size = int(element.height * 0.8)
                if font_size <= 0:
                    font_size = 1
                font_name = element.font
                font_index = 0
                if ':' in font_name:
                    font_name, font_index = font_name.split(':')
                    font_index = int(font_index)
                font = ImageFont.truetype(font_name, size=font_size, index=font_index)
            except OSError:
                print(f"Warning: Font file not found at {element.font}. Using default font.")
                font = ImageFont.load_default()

            text_width, _ = draw.textbbox((0,0), element.text, font=font)[2:]

            if text_width > active_width:
                scale_factor = active_width / text_width
                font_size = int(font_size * scale_factor)
            
            if font_size < min_font_size:
                min_font_size = font_size
        group_font_sizes[key] = min_font_size

    # Calculate final rendered heights
    rendered_heights = []
    for element in poster.elements:
        if isinstance(element, TextLine):
            font_size = group_font_sizes[(element.size_modifier, element.font)]
            try:
                font_name = element.font
                font_index = 0
                if ':' in font_name:
                    font_name, font_index = font_name.split(':')
                    font_index = int(font_index)
                font = ImageFont.truetype(font_name, size=font_size, index=font_index)
            except OSError:
                print(f"Warning: Font file not found at {element.font}. Using default font.")
                font = ImageFont.load_default()
            _, text_height = draw.textbbox((0,0), element.text, font=font)[2:]
            rendered_heights.append(text_height)
        else:
            rendered_heights.append(element.height)

    # Calculate total rendered height and extra whitespace
    total_rendered_height = sum(rendered_heights)
    extra_whitespace = active_height - total_rendered_height
    y_cursor = margin_y + extra_whitespace / 2

    # Render all elements
    for i, element in enumerate(poster.elements):
        if isinstance(element, TextLine):
            font_size = group_font_sizes[(element.size_modifier, element.font)]
            try:
                font_name = element.font
                font_index = 0
                if ':' in font_name:
                    font_name, font_index = font_name.split(':')
                    font_index = int(font_index)
                font = ImageFont.truetype(font_name, size=font_size, index=font_index)
            except OSError:
                print(f"Warning: Font file not found at {element.font}. Using default font.")
                font = ImageFont.load_default()

            text_width, text_height = draw.textbbox((0,0), element.text, font=font)[2:]
            
            x = margin_x
            if element.justification == 'center':
                x = (poster.width - text_width) / 2
            elif element.justification == 'right':
                x = poster.width - margin_x - text_width

            draw.text((x, y_cursor), element.text, fill=element.color, font=font)
            y_cursor += text_height
        elif isinstance(element, BlankLine):
            y_cursor += element.height
        elif isinstance(element, ImageElement):
            try:
                img = Image.open(element.path)
                
                if element.width and not element.height:
                    if str(element.width).endswith('%'):
                        new_width = int((poster.width - 2 * margin_x) * (float(str(element.width)[:-1]) / 100))
                    else:
                        new_width = int(element.width)
                    aspect_ratio = img.height / img.width
                    new_height = int(new_width * aspect_ratio)
                    element.height = new_height
                
                img.thumbnail((poster.width - 2 * margin_x, element.height))
                x = (poster.width - img.width) / 2
                if img.mode == 'RGBA':
                    image.paste(img, (int(x), int(y_cursor)), img)
                else:
                    image.paste(img, (int(x), int(y_cursor)))
                y_cursor += element.height
            except IOError:
                raise IOError(f"Error: Image file not found at {element.path}. Please ensure the image exists and the path is correct.")

    image.save(output_filename)

def main():
    parser = argparse.ArgumentParser(description='Create posters from a text file.')
    parser.add_argument('input_file', nargs='?', help='The input file for the poster.')
    parser.add_argument('-o', '--output', help='The output file name.', default='output.png')
    parser.add_argument('--size', help='The size of the output image in the format <width>x<height>.')
    parser.add_argument('--list-common-fonts', action='store_true', help='List common fonts and exit.')
    parser.add_argument('--list-fonts', action='store_true', help='List all available fonts and exit.')
    parser.add_argument('--preview', action='store_true', help='Preview the generated image.')
    parser.add_argument('--margin', help='The margin for the poster as a percentage or in pixels.')
    args = parser.parse_args()

    if args.list_common_fonts:
        list_fonts(common_only=True)
        return

    if args.list_fonts:
        list_fonts()
        return

    if not args.input_file:
        parser.error('the following arguments are required: input_file')

    font_map = get_font_map()
    poster = Poster()

    with open(args.input_file, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if line.startswith('!'):
            parts = line[1:].split(' ', 1)
            command = parts[0]
            if command == 'font':
                font_name = parts[1]
                if font_name in font_map:
                    poster.font = font_map[font_name]
                else:
                    poster.font = font_name
            elif command == 'size':
                poster.width, poster.height = map(int, parts[1].split('x'))
            elif command == 'margin':
                margin_str = parts[1]
                if margin_str.endswith('%'):
                    poster.margin = float(margin_str[:-1]) / 100
                else:
                    poster.margin = int(margin_str)
            elif command == 'background_color':
                poster.background_color = parts[1]
            elif command == 'background_image':
                poster.background_image = parts[1]
            continue

        element = parse_line(line, poster)
        if element:
            poster.elements.append(element)

    render_poster(poster, args.output)

    if args.preview:
        if os.name == 'posix':
            subprocess.run(['xdg-open', args.output])
        elif os.name == 'mac':
            subprocess.run(['open', args.output])
        elif os.name == 'nt':
            os.startfile(args.output)


if __name__ == '__main__':
    main()