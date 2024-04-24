import os
import sys
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageOps

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

OUTPUT_PATH = resource_path(os.path.join('output', 'address_labels.pdf'))
SINGLE_ADDRESS_LABEL = resource_path(os.path.join('output', 'single_address_label.png'))

def create_single_label(dpi=300):
    corner_radius = 10  # Radius of the rounded corners, scaled by DPI
    x1, y1, x2, y2 = 20, 330, 220, 395  # Original cropping coordinates

    pdf_document = fitz.open(OUTPUT_PATH)
    page = pdf_document[0]
    pix = page.get_pixmap(dpi=dpi)
    image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

    # Adjusting crop coordinates based on DPI scaling
    cropped_image = image.crop((x1 * dpi / 72, y1 * dpi / 72, x2 * dpi / 72, y2 * dpi / 72))

    # Create a mask for rounded corners
    mask = Image.new("L", cropped_image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), cropped_image.size], corner_radius * dpi / 72, fill=255)

    # Apply rounded corners to the cropped image
    rounded_image = ImageOps.fit(cropped_image, mask.size, centering=(0.5, 0.5))
    rounded_image.putalpha(mask)

    # Correctly applying the mask to create rounded corners
    final_image = Image.alpha_composite(Image.new("RGBA", cropped_image.size, (255, 255, 255, 0)), rounded_image)

    final_image.save(SINGLE_ADDRESS_LABEL, "PNG")
    pdf_document.close()

if __name__ == "__main__":
    create_single_label()
