from PIL import Image, ImageDraw, ImageFont
import os
import io 

def condense_number(n):
    if n >= 1000000:
        return f"{n / 1000000:.1f}M"
    elif n >= 1000:
        return f"{n / 1000:.1f}K"
    else:
        return str(int(n))

def create_stock_alert_image(ticker, price, multiplier, float_value, volume, output_filename=None):
    """
    Creates a condensed stock alert image with a smooth gradient background.
    Can either save to a file or return image bytes in memory.

    Args:
        ticker (str): The stock ticker symbol.
        price (float): The current price.
        multiplier (float): The multiplier value.
        float_value (float): The float value.
        volume (float): The volume.
        output_filename (str, optional): If provided, saves the image to this filename.
                                         If None, returns image bytes. Defaults to None.

    Returns:
        bytes or None: If output_filename is None, returns the image as PNG bytes.
                       Otherwise, returns None.
    """

    # Define colors
    COLOR_BG_DARK_START = "#1A202C"  # A very dark gray (similar to Tailwind gray-900)
    COLOR_BG_DARK_END = "#4181b4"    # The vibrant teal provided by you for the flare
    COLOR_FLOAT = "#cce1fc"
    COLOR_PALETTE_MULT = "#24948c"
    COLOR_TEXT_WHITE = "#FFFFFF"
    COLOR_ACCENT_EMERALD = "#49b9de"
    COLOR_ACCENT_BLUE = "#60A5FA"
    COLOR_ACCENT_TEAL = "#2DD4BF"
    COLOR_BORDER = "#4B5563"

    # Image dimensions
    img_width = 550
    img_height = 300
    border_width = 5
    padding = 20

    # Create a new image (initial color is irrelevant as it's immediately overwritten by gradient)
    img = Image.new('RGB', (img_width, img_height))
    draw = ImageDraw.Draw(img)
    
    # Create a gradient background: blending colors smoothly over the entire height
    start_r = int(COLOR_BG_DARK_START.lstrip('#')[0:2], 16)
    start_g = int(COLOR_BG_DARK_START.lstrip('#')[2:4], 16)
    start_b = int(COLOR_BG_DARK_START.lstrip('#')[4:6], 16)

    end_r = int(COLOR_BG_DARK_END.lstrip('#')[0:2], 16)
    end_g = int(COLOR_BG_DARK_END.lstrip('#')[2:4], 16)
    end_b = int(COLOR_BG_DARK_END.lstrip('#')[4:6], 16)

    for y in range(img_height):
        # Calculate blend factor across the entire image height
        blend_factor = y / img_height
        
        current_r = int(start_r * (1 - blend_factor) + end_r * blend_factor)
        current_g = int(start_g * (1 - blend_factor) + end_g * blend_factor)
        current_b = int(start_b * (1 - blend_factor) + end_b * blend_factor)
        
        draw.line([(0, y), (img_width, y)], fill=(current_r, current_g, current_b))


    # --- Load Fonts ---
    try:
        if os.name == 'nt':
            font_path_bold = "arialbd.ttf"
            font_path_regular = "arial.ttf"
        elif os.name == 'posix':
            font_path_bold = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
            if not os.path.exists(font_path_bold):
                font_path_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            font_path_regular = "/System/Library/Fonts/Supplemental/Arial.ttf"
            if not os.path.exists(font_path_regular):
                font_path_regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        else:
            font_path_bold = None
            font_path_regular = None

        font_ticker = ImageFont.truetype(font_path_bold, 60) if font_path_bold and os.path.exists(font_path_bold) else ImageFont.load_default(60)
        font_stats = ImageFont.truetype(font_path_regular, 28) if font_path_regular and os.path.exists(font_path_regular) else ImageFont.load_default(28)
        font_alert = ImageFont.truetype(font_path_bold, 30) if font_path_bold and os.path.exists(font_path_bold) else ImageFont.load_default(30)

    except IOError:
        print("Could not load specific fonts, using default PIL fonts. For better appearance, consider installing Arial or DejaVuSans, or provide custom .ttf files.")
        font_ticker = ImageFont.load_default(60)
        font_stats = ImageFont.load_default(28)
        font_alert = ImageFont.load_default(30)

    # --- Draw Elements ---

    # "Momentum Alert" (Top Center)
    alert_text = "Momentum Alert"
    alert_bbox = draw.textbbox((0, 0), alert_text, font=font_alert)
    alert_x = (img_width - (alert_bbox [2] - alert_bbox [0])) // 2
    alert_y = padding
    draw.text((alert_x, alert_y), alert_text, font=font_alert, fill=COLOR_ACCENT_BLUE)

    # Ticker Symbol (Center)
    ticker_text = ticker
    ticker_bbox = draw.textbbox((0, 0), ticker_text, font=font_ticker)
    ticker_x = (img_width - (ticker_bbox [2] - ticker_bbox [0])) // 2
    ticker_y = alert_y + (alert_bbox [3] - alert_bbox [1]) + 50 # Increased spacing after alert
    draw.text((ticker_x, ticker_y), ticker_text, font=font_ticker, fill=COLOR_ACCENT_EMERALD)

    # Grouped Stats (Bottom Center)
    line_height = font_stats.getbbox("Sample Text")[3] - font_stats.getbbox("Sample Text")[1]
    # Calculate starting Y for stats group, considering total height of 3 lines of text + spacing
    total_stats_height = (line_height * 3) + (5 * 2) + 10 # 3 lines, 2 small gaps, 1 large gap
    stats_y = img_height - padding - total_stats_height # Adjusted initial Y for more space
    stats_x_center = img_width // 2

    # Price
    price_text = f"${price:.2f}" # Removed "Price: " label
    price_bbox = draw.textbbox((0, 0), price_text, font=font_stats)
    price_x = stats_x_center - (price_bbox [2] - price_bbox [0]) // 2
    draw.text((price_x, stats_y), price_text, font=font_stats, fill=COLOR_TEXT_WHITE)
    stats_y += line_height + 5

    # Multiplier (corrected label)
    multiplier_text = f"Mult: {multiplier:.1f}x" # Corrected label back to "Mult"
    multiplier_bbox = draw.textbbox((0, 0), multiplier_text, font=font_stats)
    multiplier_x = stats_x_center - (multiplier_bbox [2] - multiplier_bbox [0]) // 2
    draw.text((multiplier_x, stats_y), multiplier_text, font=font_stats, fill=COLOR_PALETTE_MULT)
    stats_y += line_height + 20 # Larger gap before float/volume

    # Float and Volume (Side by side below Price and Multiplier)
    float_condensed = condense_number(float_value)
    volume_condensed = condense_number(volume)

    float_text = f"Float: {float_condensed}"
    volume_text = f"Volume: {volume_condensed}"

    float_bbox = draw.textbbox((0, 0), float_text, font=font_stats)
    volume_bbox = draw.textbbox((0, 0), volume_text, font=font_stats)

    float_text_width = float_bbox[2] - float_bbox[0]
    volume_text_width = volume_bbox[2] - volume_bbox[0]

    gap_between_float_volume = 30
    combined_width = float_text_width + gap_between_float_volume + volume_text_width

    float_x = stats_x_center - combined_width // 2
    volume_x = float_x + float_text_width + gap_between_float_volume

    # Changed colors back to ACCENT_BLUE for visibility
    draw.text((float_x, stats_y), float_text, font=font_stats, fill=COLOR_FLOAT)
    draw.text((volume_x, stats_y), volume_text, font=font_stats, fill=COLOR_FLOAT)


    # --- Return Image Data or Save to File ---
    if output_filename:
        img.save(output_filename)
        print(f"Image saved as {output_filename}")
        return None
    else:
        # Save image to a bytes buffer in memory
        byte_arr = io.BytesIO()
        img.save(byte_arr, format='PNG')
        byte_arr.seek(0) # Rewind to the beginning of the buffer
        print("Image data generated in memory.")
        return byte_arr.getvalue()





    