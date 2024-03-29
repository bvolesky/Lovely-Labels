import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageOps

def create_single_label(dpi=300):
    pdf_file_path = "output/address_labels.pdf"
    output_file_path = "output/single_address_label.png"
    corner_radius = 10  # Radius of the rounded corners, scaled by DPI
    x1, y1, x2, y2 = 20, 330, 220, 395  # Original cropping coordinates

    pdf_document = fitz.open(pdf_file_path)
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

    final_image.save(output_file_path, "PNG")
    pdf_document.close()

if __name__ == "__main__":
    create_single_label()
