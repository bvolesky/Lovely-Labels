import os
import sys
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

OUTPUT_PATH = resource_path(os.path.join('output', 'address_labels.pdf'))
DEFAULT_JSON = resource_path(os.path.join('data', 'default.json'))
USER_DATA_JSON = resource_path(os.path.join('data','user_data.json'))

class Sheet:
    def __init__(
        self,
        output_path,
        width=8.5,
        height=11,
        x_margin=0.19,
        y_margin=0.5,
        line_width=0.3,
        margin_outline=False,
    ):
        self.width = width
        self.height = height
        self.x_margin = x_margin
        self.y_margin = y_margin
        self.canvas = canvas.Canvas(output_path, pagesize=letter)
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
        self.num_rows = 10
        self.num_cols = 3
        self.horizontal_spacing = 0.118
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
        width=2.625,
        height=1,
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
            self, Image(data["image"]), image_outline=self.image_outline
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
        padding=0.15,
    ):
        self.label = label
        self.padding = padding
        self.width = label.width * 0.5
        self.height = label.height - 2 * self.padding
        self.x = label.x + self.width - self.padding + 0.1
        self.y = label.y + self.padding
        self.canvas = label.canvas
        self.line_height = (1 - 2 * 0.15) / 3
        self.line_spacing = 0
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
        height=0.23333333333,
    ):
        self.address_group = address_group
        self.x = x
        self.y = y
        self.text = text
        self.height = height
        self.width = address_group.width
        self.canvas = address_group.canvas
        self.address_lines_outline = address_lines_outline
        self.text_x_offset = 0.025
        self.text_y_offset = 0.05

    def draw(self):
        font_name = "Helvetica"
        font_size = 9
        text_width = stringWidth(self.text, font_name, font_size)

        # Adjust font size to fit the text within the width of the address line
        while (
            text_width > (self.width - 2 * self.text_x_offset) * inch and font_size > 1
        ):
            font_size -= 0.1  # Decrease font size
            text_width = stringWidth(self.text, font_name, font_size)

        self.canvas.setFont(font_name, font_size)
        self.canvas.drawString(
            (self.x + self.text_x_offset) * inch,
            (self.y + self.text_y_offset) * inch,
            self.text,
        )

        if self.address_lines_outline:
            self.canvas.rect(
                self.x * inch, self.y * inch, self.width * inch, self.height * inch
            )


class ImageGroup:
    def __init__(self, label, image, image_outline=False, padding=0.15):
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


def create_pdf(OUTPUT_PATH=OUTPUT_PATH):
    DEBUG = False
    if DEBUG:
        data = json.load(open(DEFAULT_JSON))

    else:
        data = json.load(open(USER_DATA_JSON))

    line_data = [
        data["first"] + " " + data["last"],
        data["address"],
        data["city"] + ", " + data["state"] + " " + data["zip"],
    ]

    label_data = {"lines": line_data, "image": data["image"]}
    my_sheet = Sheet(OUTPUT_PATH)
    LabelMatrix(my_sheet, label_data)
    my_sheet.canvas.save()


if __name__ == "__main__":
    create_pdf()
