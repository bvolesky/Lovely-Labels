import fitz  # PyMuPDF
from PIL import Image

# PDF file path
pdf_file_path = "output/address_labels.pdf"

# Output JPG file path
output_file_path = "output/single_address_label.jpg"

# Specify the coordinates for cropping (replace with your values)
x1, y1, x2, y2 = 20, 330, 225, 395  # left, upper, right, lower

# Open the PDF file
pdf_document = fitz.open(pdf_file_path)

# Select the first page (you can change this if necessary)
page = pdf_document[0]

# Render the page as an image
pix = page.get_pixmap()

# Create a new image from the PDF content
image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

# Crop the image to the specified coordinates
cropped_image = image.crop((x1, y1, x2, y2))

# Save the cropped image as a JPG file
cropped_image.save(output_file_path, "JPEG")

# Close the PDF document
pdf_document.close()

print(f"Single address label saved as {output_file_path}")
