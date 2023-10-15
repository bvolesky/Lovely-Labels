import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image


class Label:
    def __init__(
        self, first_name, last_name, address, city, state, zip_code, image_path
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.image = self.process_png_image(image_path)

    def process_png_image(self, image_path):
        image = Image.open(image_path)
        if image.mode == "RGBA":
            white_background = Image.new("RGBA", image.size, (255, 255, 255))
            image = Image.alpha_composite(white_background, image).convert("RGB")

        new_height = 0.6 * label_height
        aspect_ratio = image.width / image.height
        new_width = aspect_ratio * new_height
        image = image.resize((int(new_width), int(new_height)))
        image.save("resized_image.png", "PNG", optimize=True)

        return image


class Sheet:
    def __init__(self, filename="labels.pdf", pagesize=letter):
        self.c = canvas.Canvas(filename, pagesize=pagesize)
        self.c.setFont("Helvetica", 12)

    def draw_label(self, x, y, label):
        # Draw the image (logo) towards the left
        self.c.drawImage(
            "resized_image.png",
            x,
            y + (label_height - label.image.height) / 2,
            # Center the image vertically within the label
            width=label.image.width,
            height=label.image.height,
        )

        # Set the starting x-coordinate for the text based on the image width and a small gap
        text_x = x + label.image.width + 10  # 10 points spacing between image and text

        # Draw the text next to the image
        self.c.drawString(
            text_x, y + label_height - 30, label.first_name + " " + label.last_name
        )
        self.c.drawString(text_x, y + label_height - 45, label.address)
        self.c.drawString(
            text_x,
            y + label_height - 60,
            f"{label.city}, {label.state} {label.zip_code}",
        )

    def generate_labels(self, label):
        for column in range(num_across):
            for row in range(num_down):
                x = side_margin + column * (label_width + 10)  # Add gap between labels
                y = top_margin + (num_down - 1 - row) * label_height
                self.draw_label(x, y, label)

    def save(self):
        self.c.save()


inch_to_points = 72
label_width = 2.63 * inch_to_points
label_height = 1 * inch_to_points
top_margin = 0.5 * inch_to_points
side_margin = 0.19 * inch_to_points
num_across = 3
num_down = 10

label = Label(
    "Johnny", "Appleseed", "123 Main Street", "Springfield", "KS", "66203", "A.png"
)
sheet = Sheet()

sheet.generate_labels(label)
sheet.save()
os.system("start labels.pdf")