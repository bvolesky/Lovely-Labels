import json

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth

DEBUG = False
if DEBUG:
    data = json.load(open('data/default.json'))

else:
    # Get user input for the data
    data = {}
    data["first_name"] = input("Enter first name: ")
    data["last_name"] = input("Enter last name: ")
    data["address"] = input("Enter address: ")
    data["city"] = input("Enter city: ")
    data["state"] = input("Enter state: ")
    data["zip"] = input("Enter zip code: ")
    data["image_path"] = f'images/letters/{data["last_name"][0].upper()}.jpg'

line_data = [
    data["first_name"] + " " + data["last_name"],
    data["address"],
    data["city"] + ", " + data["state"] + " " + data["zip"],
]


label_data = {"lines": line_data, "image_path": data["image_path"]}


# Global Constants
DEFAULT_WIDTH = 8.5
DEFAULT_HEIGHT = 11
DEFAULT_X_MARGIN = 0.19
DEFAULT_Y_MARGIN = 0.5
DEFAULT_LINE_WIDTH = 0.3

NUM_ROWS = 10
NUM_COLS = 3
HORIZONTAL_SPACING = 0.118
LABEL_WIDTH = 2.625
LABEL_HEIGHT = 1
ADDRESS_GROUP_PADDING = 0.15
IMAGE_GROUP_PADDING = 0.15
ADDRESS_LINE_HEIGHT = (LABEL_HEIGHT - 2 * ADDRESS_GROUP_PADDING) / len(line_data)
ADDRESS_LINE_SPACING = 0.0

FONT_NAME = "Helvetica"
FONT_SIZE = 9 - (len(line_data) - 3)
TEXT_X_OFFSET = 0.025
TEXT_Y_OFFSET = 0.05


# Usage
MARGIN_OUTLINE = False
LABEL_OUTLINE = False
ADDRESS_OUTLINE = False
ADDRESS_LINES_OUTLINE = False
IMAGE_OUTLINE = False

# Output path
OUTPUT_PATH = "output/address_labels.pdf"
if all(
    [
        MARGIN_OUTLINE,
        LABEL_OUTLINE,
        ADDRESS_OUTLINE,
        ADDRESS_LINES_OUTLINE,
        IMAGE_OUTLINE,
    ]
):
    OUTPUT_PATH = "output/address_labels_with_outlines.pdf"


class Sheet:
    def __init__(
        self,
        width=DEFAULT_WIDTH,
        height=DEFAULT_HEIGHT,
        x_margin=DEFAULT_X_MARGIN,
        y_margin=DEFAULT_Y_MARGIN,
        line_width=DEFAULT_LINE_WIDTH,
        margin_outline=False,
    ):
        self.width = width
        self.height = height
        self.x_margin = x_margin
        self.y_margin = y_margin
        self.canvas = canvas.Canvas(OUTPUT_PATH, pagesize=letter)
        self.canvas.setLineWidth(line_width)
        self.margin_outline = margin_outline
        self._draw_margins()

    def _draw_margins(self):
        if self.margin_outline:
            x, y, width, height = (
                self.x_margin,
                self.y_margin,
                self.width - 2 * self.x_margin,
                self.height - 2 * self.y_margin,
            )
            self.canvas.rect(x * inch, y * inch, width * inch, height * inch)


class LabelMatrix:
    def __init__(
        self,
        sheet,
        data,
        label_outline=False,
        address_outline=False,
        address_lines_outline=False,
        image_outline=False,
    ):
        self.num_rows = NUM_ROWS
        self.num_cols = NUM_COLS
        self.horizontal_spacing = HORIZONTAL_SPACING
        self.sheet = sheet
        self.sample_label = self._create_sample_label(data)
        self.x = sheet.x_margin
        self.y = sheet.y_margin
        self.width = sheet.width - 2 * sheet.x_margin
        self.height = sheet.height - 2 * sheet.y_margin
        self.canvas = sheet.canvas
        self.matrix = []
        self.data = data
        self.label_outline = label_outline
        self.address_outline = address_outline
        self.address_lines_outline = address_lines_outline
        self.image_outline = image_outline
        self._create_matrix()

    def _create_sample_label(self, data):
        return Label(self.sheet, self.sheet.x_margin, self.sheet.y_margin, data)

    def _create_matrix(self):
        self.matrix = [
            [
                Label(
                    self.sheet,
                    self.x + i * (self.sample_label.width + self.horizontal_spacing),
                    self.y + j * self.sample_label.height,
                    self.data,
                    self.label_outline,
                    self.address_outline,
                    self.address_lines_outline,
                    self.image_outline,
                )
                for i in range(self.num_cols)
            ]
            for j in range(self.num_rows)
        ]
        self._draw()

    def _draw(self, location=False):
        if not location:
            for row in self.matrix:
                for label in row:
                    label.draw()
        else:
            # location is a tuple of (row, col)
            self.matrix[location[0]][location[1]].draw()


class Label:
    def __init__(
        self,
        label_group,
        x,
        y,
        data,
        label_outline=False,
        address_outline=False,
        address_lines_outline=False,
        image_outline=False,
        width=LABEL_WIDTH,
        height=LABEL_HEIGHT,
    ):
        self.label_group = label_group
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.canvas = label_group.canvas
        self.label_outline = label_outline
        self.address_outline = address_outline
        self.address_lines_outline = address_lines_outline
        self.image_outline = image_outline
        self.image_group = ImageGroup(
            self, Image(data["image_path"]), image_outline=self.image_outline
        )
        self.address_group = AddressGroup(
            self,
            data,
            address_outline=self.address_outline,
            address_lines_outline=self.address_lines_outline,
        )

    def draw(self):
        self.image_group.draw()
        self.address_group.draw()
        if self.label_outline:
            self.canvas.rect(
                self.x * inch, self.y * inch, self.width * inch, self.height * inch
            )


class AddressGroup:
    def __init__(
        self,
        label,
        data,
        address_outline,
        address_lines_outline,
        padding=ADDRESS_GROUP_PADDING,
    ):
        self.label = label
        self.padding = padding
        self.width = label.width * 0.5
        self.height = label.height - 2 * self.padding
        self.x = label.x + self.width - self.padding
        self.y = label.y + self.padding
        self.canvas = label.canvas
        self.line_height = ADDRESS_LINE_HEIGHT
        self.line_spacing = ADDRESS_LINE_SPACING
        self.address_lines = []
        self.data = data
        self.address_outline = address_outline
        self.address_lines_outline = address_lines_outline
        self._create_address_lines(self.data)

    def _create_address_lines(self, line_data):
        for i, data in enumerate(line_data["lines"][::-1]):
            y = self.y + i * (self.line_height + self.line_spacing)
            line = AddressLine(self, self.x, y, data, self.address_lines_outline)
            self.address_lines.append(line)

    def draw(self):
        for line in self.address_lines:
            line.draw()

        if self.address_outline:
            self.canvas.rect(
                self.x * inch, self.y * inch, self.width * inch, self.height * inch
            )

class AddressLine:
    def __init__(
        self,
        address_group,
        x,
        y,
        text,
        address_lines_outline,
        height=ADDRESS_LINE_HEIGHT,
    ):
        self.address_group = address_group
        self.x = x
        self.y = y
        self.text = text
        self.height = height
        self.width = address_group.width
        self.canvas = address_group.canvas
        self.address_lines_outline = address_lines_outline

    def draw(self):
        font_size = FONT_SIZE
        text_width = stringWidth(self.text, FONT_NAME, font_size)

        # Adjust font size to fit the text within the width of the address line
        while text_width > (self.width - 2 * TEXT_X_OFFSET) * inch and font_size > 1:
            font_size -= 0.1  # Decrease font size
            text_width = stringWidth(self.text, FONT_NAME, font_size)

        self.canvas.setFont(FONT_NAME, font_size)
        self.canvas.drawString(
            (self.x + TEXT_X_OFFSET) * inch,
            (self.y + TEXT_Y_OFFSET) * inch,
            self.text,
        )

        if self.address_lines_outline:
            self.canvas.rect(
                self.x * inch, self.y * inch, self.width * inch, self.height * inch
            )



class ImageGroup:
    def __init__(self, label, image, image_outline=False, padding=IMAGE_GROUP_PADDING):
        self.label = label
        self.padding = padding
        self.width = label.width * 0.5 - 2 * self.padding
        self.height = label.height - 2 * self.padding
        self.x = label.x + self.padding
        self.y = label.y + self.padding
        self.canvas = label.canvas
        self.image = image
        self.image_outline = image_outline

    def draw(self):
        self.image.draw(self.canvas, self.x, self.y, self.width, self.height)
        if self.image_outline:
            self.canvas.rect(
                self.x * inch, self.y * inch, self.width * inch, self.height * inch
            )


class Image:
    def __init__(self, image_path):
        self.image_path = image_path

    def draw(self, canvas, x, y, width, height):
        canvas.drawImage(
            self.image_path, x * inch, y * inch, width * inch, height * inch
        )


def main():
    my_sheet = Sheet(margin_outline=MARGIN_OUTLINE)
    LabelMatrix(
        my_sheet,
        label_data,
        label_outline=LABEL_OUTLINE,
        address_outline=ADDRESS_OUTLINE,
        address_lines_outline=ADDRESS_LINES_OUTLINE,
        image_outline=IMAGE_OUTLINE,
    )
    my_sheet.canvas.save()


if __name__ == "__main__":
    main()
