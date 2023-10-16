import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image, ImageOps

class Label:
    def __init__(self, first_name, last_name, address, city, state, zip_code, image_path):
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.image = self.process_image(image_path)

    def process_image(self, image_path):
        image = Image.open(image_path)
        new_width = IMAGE_SIZE * INCH_TO_POINTS
        aspect_ratio = image.width / image.height
        new_height = new_width / aspect_ratio
        image = ImageOps.fit(image, (int(new_width), int(new_height)))
        return image

class Sheet:
    def __init__(self, file_name, pagesize=letter):
        self.file_name = file_name
        self.pagesize = pagesize
        self.c = canvas.Canvas(self.file_name, pagesize=self.pagesize)
        self.c.setFont(FONT_NAME, FONT_SIZE)

    def draw_label(self, x, y, label):
        self.c.drawInlineImage(
            label.image,
            x,
            y + (LABEL_HEIGHT - label.image.height) / IMAGE_Y_DIVISION,
            width=label.image.width,
            height=label.image.height,
        )
        text_x = x + label.image.width + IMAGE_TEXT_SPACING_X
        self.c.drawString(text_x, y + LABEL_HEIGHT - LINE_1_POSITION_Y, f"{label.first_name} {label.last_name}")
        self.c.drawString(text_x, y + LABEL_HEIGHT - LINE_2_POSITION_Y, label.address)
        self.c.drawString(text_x, y + LABEL_HEIGHT - LINE_3_POSITION_Y, f"{label.city}, {label.state} {label.zip_code}")

    def generate_labels(self, label):
        for column in range(NUM_ACROSS):
            for row in range(NUM_DOWN):
                x = SIDE_MARGIN + column * (LABEL_WIDTH + GAP_BETWEEN_LABELS_X)
                y = TOP_MARGIN + (NUM_DOWN - ALL_LABEL_GROUP_POSITION_Y - row) * LABEL_HEIGHT
                self.draw_label(x, y, label)

    def save(self):
        self.c.save()
        os.system(f"start {self.file_name}")

# Constants
FILE_NAME = "labels.pdf"
INCH_TO_POINTS = 72
LABEL_WIDTH = 2.63 * INCH_TO_POINTS
LABEL_HEIGHT = 1 * INCH_TO_POINTS
TOP_MARGIN = 0.5 * INCH_TO_POINTS
SIDE_MARGIN = 0.19 * INCH_TO_POINTS
NUM_ACROSS = 3
NUM_DOWN = 10
IMAGE_SIZE = 0.85
FONT_NAME = "Helvetica"
FONT_SIZE = 10
IMAGE_Y_DIVISION = 2
IMAGE_TEXT_SPACING_X = 10
GAP_BETWEEN_LABELS_X = 10
ALL_LABEL_GROUP_POSITION_Y = 1
SPACING = 15
LINE_1_POSITION_Y = 25
LINE_2_POSITION_Y = LINE_1_POSITION_Y + SPACING
LINE_3_POSITION_Y = LINE_2_POSITION_Y + SPACING

label = Label(
    "Johnny", "Appleseed", "123 Main Street", "Springfield", "KS", "66203", "cat.jpg"
)
sheet = Sheet(FILE_NAME)
sheet.generate_labels(label)
sheet.save()
