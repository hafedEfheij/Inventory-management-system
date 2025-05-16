import os
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import base64
from PIL import Image, ImageDraw, ImageFont
import random
import string

def generate_random_barcode(length=12):
    """Generate a random barcode number of specified length"""
    return ''.join(random.choices(string.digits, k=length))

def generate_barcode_base64(barcode_value, barcode_type='code128'):
    """
    Generate a barcode image and return it as a base64 encoded string
    
    Args:
        barcode_value (str): The value to encode in the barcode
        barcode_type (str): The type of barcode to generate (default: code128)
        
    Returns:
        str: Base64 encoded string of the barcode image
    """
    if not barcode_value:
        barcode_value = generate_random_barcode()
    
    # Create a BytesIO object to store the image
    output = BytesIO()
    
    # Create the barcode
    try:
        barcode_class = barcode.get_barcode_class(barcode_type)
        barcode_instance = barcode_class(barcode_value, writer=ImageWriter())
        barcode_instance.write(output)
    except Exception as e:
        # If there's an error, return None
        print(f"Error generating barcode: {e}")
        return None
    
    # Get the image data and encode it as base64
    output.seek(0)
    encoded_image = base64.b64encode(output.getvalue()).decode('utf-8')
    
    return encoded_image

def generate_barcode_file(barcode_value, filename, barcode_type='code128'):
    """
    Generate a barcode image and save it to a file
    
    Args:
        barcode_value (str): The value to encode in the barcode
        filename (str): The filename to save the barcode to (without extension)
        barcode_type (str): The type of barcode to generate (default: code128)
        
    Returns:
        str: The path to the saved barcode image
    """
    if not barcode_value:
        barcode_value = generate_random_barcode()
    
    # Create the barcode
    try:
        barcode_class = barcode.get_barcode_class(barcode_type)
        barcode_instance = barcode_class(barcode_value, writer=ImageWriter())
        
        # Ensure the static/barcodes directory exists
        os.makedirs('static/barcodes', exist_ok=True)
        
        # Save the barcode to a file
        filepath = barcode_instance.save(f'static/barcodes/{filename}')
        return filepath
    except Exception as e:
        # If there's an error, return None
        print(f"Error generating barcode: {e}")
        return None

def get_barcode_types():
    """
    Get a list of available barcode types
    
    Returns:
        list: List of available barcode types
    """
    return [
        ('code128', 'Code 128'),
        ('ean13', 'EAN-13'),
        ('ean8', 'EAN-8'),
        ('upca', 'UPC-A'),
        ('isbn13', 'ISBN-13'),
        ('isbn10', 'ISBN-10'),
        ('issn', 'ISSN'),
        ('code39', 'Code 39'),
        ('pzn', 'PZN'),
        ('gs1', 'GS1'),
        ('gtin', 'GTIN'),
        ('ean', 'EAN'),
        ('jan', 'JAN'),
        ('upc', 'UPC')
    ]
