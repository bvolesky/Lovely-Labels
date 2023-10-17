from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


class Sheet:
    def __init__(
        self,
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
        self.canvas = canvas.Canvas("address_labels.pdf", pagesize=letter)
        self.canvas.setLineWidth(line_width)
        self.margin_outline = margin_outline
        self.draw_margins()

    def draw_margins(self, fill=False):
        if self.margin_outline:
            self.canvas.rect(
                self.x_margin * inch,
                self.y_margin * inch,
                (self.width - 2 * self.x_margin) * inch,
                (self.height - 2 * self.y_margin) * inch,
            )
        if fill:
            self.canvas.setFillColorRGB(0, 0, 0)
            self.canvas.rect(
                self.x_margin * inch,
                self.y_margin * inch,
                (self.width - 2 * self.x_margin) * inch,
                (self.height - 2 * self.y_margin) * inch,
                fill=1,
            )


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
        self.label = Label(
            my_sheet, my_sheet.x_margin, my_sheet.y_margin, data, bypass=True
        )
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
        self.create_matrix()

    def create_matrix(self):
        self.matrix = [
            [
                Label(
                    self.sheet,
                    self.x + i * (self.label.width + self.horizontal_spacing),
                    self.y + j * self.label.height,
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
        self.draw()

    def draw(self, location=False, fill=False):
        if not location:
            for row in self.matrix:
                for label in row:
                    label.draw(fill)
        else:
            # location is a tuple of (row, col)
            self.matrix[location[0]][location[1]].draw(fill)


# Create a class called Label that is the size of a label in the matrix
class Label:
    # Size of label is for AVERY 5160
    # Labels should have 0.118 spacing between them horizontally on the right
    # and NO spacing vertically

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
        bypass=False,
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
        self.address_group = AddressGroup(
            self,
            data,
            address_outline=self.address_outline,
            address_lines_outline=self.address_lines_outline,
        )
        self.image_group = ImageGroup(
            self, Image(data["image_path"]), image_outline=self.image_outline
        )
        if not bypass:
            self.address_group.draw()

    def draw(self, fill=False):
        if self.label_outline:
            self.canvas.rect(
                self.x * inch, self.y * inch, self.width * inch, self.height * inch
            )
        self.image_group.draw()

        if fill:
            self.canvas.setFillColorRGB(0, 0, 0)
            self.canvas.rect(
                self.x * inch,
                self.y * inch,
                self.width * inch,
                self.height * inch,
                fill=1,
            )


# Create an address group that contains all text lines inside the label
class AddressGroup:
    def __init__(
        self, label, data, address_outline, address_lines_outline, padding=0.15
    ):
        self.label = label
        self.padding = padding  # Introduce a padding for AddressGroup
        self.width = label.width * 0.5
        self.height = label.height - 2 * self.padding
        self.x = label.x + self.width - self.padding
        self.y = label.y + self.padding
        self.canvas = label.canvas
        self.line_height = 0.2
        self.line_spacing = 0.1
        self.data = data
        self.address_outline = address_outline
        self.address_lines_outline = address_lines_outline

    def draw(self, fill=False):
        if self.address_outline:
            self.canvas.rect(
                self.x * inch, self.y * inch, self.width * inch, self.height * inch
            )
        full_name = self.data["first_name"] + " " + self.data["last_name"]
        address_line_1 = full_name
        address_line_2 = self.data["address"]
        address_line_3 = (
            self.data["city"] + ", " + self.data["state"] + " " + self.data["zip"]
        )
        address_lines = [address_line_1, address_line_2, address_line_3]
        reversed_address_lines = address_lines[::-1]
        for index, item in enumerate(reversed_address_lines):
            address_line = AddressLine(
                self, index, item, address_lines_outline=self.address_lines_outline
            )
            address_line.draw(fill)

        if fill:
            self.canvas.setFillColorRGB(0, 0, 0)
            self.canvas.rect(
                self.x * inch,
                self.y * inch,
                self.width * inch,
                self.height * inch,
                fill=1,
            )


class AddressLine:
    def __init__(
        self, label, line_number, text, num_lines=3, address_lines_outline=False
    ):
        self.label = label
        self.line_number = line_number
        self.num_lines = num_lines
        self.x = label.x
        self.y = label.y + (self.line_number * (label.height / self.num_lines))
        self.width = label.width
        self.height = label.height / self.num_lines
        self.canvas = label.canvas
        self.text = Text(text)
        self.address_lines_outline = address_lines_outline

    def draw(self, fill=False):
        # Adjust the y position to center the text vertically
        self.text.draw(self.canvas, (self.x + 0.025) * inch, (self.y + 0.05) * inch)

        if self.address_lines_outline:
            self.canvas.rect(
                self.x * inch, self.y * inch, self.width * inch, self.height * inch
            )

        if fill:
            self.canvas.setFillColorRGB(0, 0, 0)
            self.canvas.rect(
                self.x * inch,
                self.y * inch,
                self.width * inch,
                self.height * inch,
                fill=1,
            )


class Text:
    def __init__(self, content):
        self.content = content
        self.font = "Helvetica"
        self.size = 10

    def draw(self, canvas, x, y):
        canvas.setFont(self.font, self.size)  # Set the font and size before drawing
        canvas.drawString(x, y, self.content)


# Create an image group class that is the container for the image, the image group is similar to the address group
class ImageGroup:
    def __init__(self, label, image, padding=0.15, image_outline=False):
        self.label = label
        self.padding = padding
        self.width = label.width * 0.35
        self.height = label.height - 2 * self.padding
        self.x = label.x + self.padding
        self.y = label.y + self.padding
        self.canvas = label.canvas
        self.image = image
        self.image_outline = image_outline

    def draw(self, fill=False):
        self.image.draw(
            self.canvas,
            self.x * inch,
            self.y * inch,
            self.width * inch,
            self.height * inch,
        )
        if self.image_outline:
            self.canvas.rect(
                self.x * inch, self.y * inch, self.width * inch, self.height * inch
            )
        if fill:
            self.canvas.setFillColorRGB(0, 0, 0)
            self.canvas.rect(
                self.x * inch,
                self.y * inch,
                self.width * inch,
                self.height * inch,
                fill=1,
            )


class Image:
    def __init__(self, path):
        self.path = path

    def draw(self, canvas, x, y, width, height):
        canvas.drawImage(self.path, x, y, width, height)


# Usage
data = {
    "first_name": "John",
    "last_name": "Doe",
    "address": "123 Main St.",
    "city": "Anytown",
    "state": "KS",
    "zip": "12345",
    "image_path": "A.jpg",
}

MARGIN_OUTLINE = True
LABEL_OUTLINE = True
ADDRESS_OUTLINE = True
ADDRESS_LINES_OUTLINE = True
IMAGE_OUTLINE = True


my_sheet = Sheet(margin_outline=MARGIN_OUTLINE)
my_label_matrix = LabelMatrix(
    my_sheet,
    data,
    label_outline=LABEL_OUTLINE,
    address_outline=ADDRESS_OUTLINE,
    address_lines_outline=ADDRESS_LINES_OUTLINE,
    image_outline=IMAGE_OUTLINE,
)
my_sheet.canvas.save()
