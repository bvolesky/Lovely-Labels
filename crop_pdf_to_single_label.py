import fitz
from PIL import Image


def create_single_label():
    pdf_file_path = "output/address_labels.pdf"
    output_file_path = "output/single_address_label.png"
    x1, y1, x2, y2 = 20, 330, 225, 395  # left, upper, right, lower
    pdf_document = fitz.open(pdf_file_path)
    page = pdf_document[0]
    pix = page.get_pixmap()
    image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    cropped_image = image.crop((x1, y1, x2, y2))
    new_width = int(cropped_image.width * 1.25)
    new_height = int(cropped_image.height * 1.25)
    resized_image = cropped_image.resize((new_width, new_height), Image.BILINEAR)
    resized_image.save(output_file_path, "PNG")
    pdf_document.close()


if __name__ == "__main__":
    create_single_label()
