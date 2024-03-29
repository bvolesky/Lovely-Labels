import fitz
from PIL import Image, ImageDraw


def create_single_label():
    pdf_file_path = "output/address_labels.pdf"
    output_file_path = "output/single_address_label.png"
    corner_radius = 10  # radius of the rounded corners
    x1, y1, x2, y2 = 20, 330, 220, 395  # left, upper, right, lower

    pdf_document = fitz.open(pdf_file_path)
    page = pdf_document[0]
    pix = page.get_pixmap()
    image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    cropped_image = image.crop((x1, y1, x2, y2))

    # Create a mask for rounded corners
    mask = Image.new("L", cropped_image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), cropped_image.size], corner_radius, fill=255)

    # Apply the rounded mask to the cropped image
    rounded_image = Image.new("RGBA", cropped_image.size)
    rounded_image.putalpha(mask)
    cropped_image.putalpha(mask)

    cropped_image.save(output_file_path, "PNG")
    pdf_document.close()


if __name__ == "__main__":
    create_single_label()
