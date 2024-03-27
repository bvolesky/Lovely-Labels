import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from tkinter import PhotoImage, filedialog
from PIL import Image, ImageTk
import json
from create_pdf import create_pdf
from crop_pdf_to_single_label import create_single_label

# Constants
FONT_NAME = "Calibri"
ENTRY_FONT = (FONT_NAME, 12)
DEFAULT_IMAGE_PATH = "output/default_single_address_label.png"
LOGO_PATH = "images/ll_small.png"
SINGLE_LABEL_IMAGE_PATH = "output/single_address_label.png"
DATA_FILE = "data/user_data.json"
APP_TITLE = "Lovely Labels"
APP_ICON = "images/ll_transparent.ico"
APP_BG_COLOR = "#F4BFC3"
PLACEHOLDERS = ["First", "Last", "Address", "City", "State", "Zip"]

# Global variables
root = ThemedTk(theme="plastik")
entries = {}
image_label = None
image_path = None


def init_ui():
    root.title(APP_TITLE)
    root.set_theme("plastik")
    root.iconbitmap(APP_ICON)
    root.geometry("400x300")
    root.configure(bg=APP_BG_COLOR)
    root.bind("<Button-1>", on_background_click)
    setup_input_frame()
    setup_label()
    setup_logo()
    setup_create_button()
    setup_upload_button()
    root.mainloop()


def setup_logo():
    logo_image = PhotoImage(file=LOGO_PATH)
    logo_label = tk.Label(root, image=logo_image, bg=APP_BG_COLOR)
    logo_label.place(relx=0.2, rely=0.2, anchor="center")
    logo_label.image = logo_image


def setup_label():
    global image_label
    image = PhotoImage(file=DEFAULT_IMAGE_PATH)
    image_label = tk.Label(root, image=image, bg=APP_BG_COLOR)
    image_label.place(relx=0.68, rely=0.23, anchor="center")
    image_label.image = image


def setup_input_frame():
    # Create a frame for the input fields
    input_frame = tk.Frame(root, bg="#F4BFC3")
    input_frame.place(relx=0.5, rely=0.43, anchor="n", relwidth=0.7, relheight=0.35)

    # Configure grid columns in the frame
    for col in range(3):
        input_frame.grid_columnconfigure(col, weight=1)

    # Define entry configurations
    entry_configs = [
        (0, 0, 1),
        (0, 1, 3),
        (1, 0, 3),
        (2, 0, 1),
        (2, 1, 1),
        (2, 2, 1),
    ]

    # Create entries using a loop
    for placeholder, (row, col, col_span) in zip(PLACEHOLDERS, entry_configs):
        entries[placeholder] = create_entry(
            input_frame, placeholder.split()[0], row, col, columnspan=col_span
        )


def on_enter(canvas, button_id):
    canvas.itemconfig(button_id, fill="#D35874")  # Darker shade of the original color


def on_leave(canvas, button_id):
    canvas.itemconfig(button_id, fill="#F06A85")  # Original color


def create_rounded_rect(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    points = [
        x1 + radius, y1,
        x1 + radius, y1,
        x2 - radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1 + radius,
        x1, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)


def setup_create_button():
    canvas = tk.Canvas(root, width=200, height=50, bg=APP_BG_COLOR,
                       highlightthickness=0)
    canvas.place(relx=0.75, rely=0.88, anchor="center")

    # Draw a rounded rectangle and get its item ID
    button_id = create_rounded_rect(canvas, 10, 10, 190, 40, radius=10, fill='#F06A85')

    # Place text over the rectangle
    canvas.create_text(100, 25, text="Create", font=(FONT_NAME, 14), fill="white")

    # Create a transparent rectangle over the button for better event handling
    canvas.create_rectangle(10, 10, 190, 40, outline="", fill="", tags="button_area")

    # Binding the click event
    def on_click(event):
        create_label_sheet()  # Call your function here

    canvas.tag_bind("button_area", "<Button-1>", on_click)

    # Bind on_enter and on_leave functions to the transparent rectangle
    canvas.tag_bind("button_area", "<Enter>",
                    lambda event, b=button_id: on_enter(canvas, b))
    canvas.tag_bind("button_area", "<Leave>",
                    lambda event, b=button_id: on_leave(canvas, b))


def setup_upload_button():
    canvas = tk.Canvas(root, width=200, height=50, bg=APP_BG_COLOR,
                       highlightthickness=0)
    canvas.place(relx=0.25, rely=0.88, anchor="center")

    button_id = create_rounded_rect(canvas, 10, 10, 190, 40, radius=10, fill='#F06A85')
    canvas.create_text(100, 25, text="Upload Image", font=(FONT_NAME, 14), fill="white")
    canvas.create_rectangle(10, 10, 190, 40, outline="", fill="",
                            tags="upload_button_area")

    canvas.tag_bind("upload_button_area", "<Button-1>", lambda event: upload_image())
    canvas.tag_bind("upload_button_area", "<Enter>",
                    lambda event, b=button_id: on_enter(canvas, b))
    canvas.tag_bind("upload_button_area", "<Leave>",
                    lambda event, b=button_id: on_leave(canvas, b))

def upload_image():
    global image_path
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        pil_img = Image.open(file_path)

        # Resize parameters - max width and height for the image, not the label
        max_width = 100
        max_height = 100
        original_width, original_height = pil_img.size

        # Calculate the correct aspect ratio
        ratio = min(max_width / original_width, max_height / original_height)
        new_size = (int(original_width * ratio), int(original_height * ratio))

        # Resize the image using LANCZOS resampling for high quality
        resized_img = pil_img.resize(new_size, Image.Resampling.LANCZOS)

        # Create a new image with the desired label size (assuming label size here)
        label_width, label_height = 100, 100  # Set these to your label's dimensions
        new_img = Image.new("RGBA", (label_width, label_height), (255, 255, 255, 0))
        # Calculate position to paste resized image in the center
        x1 = (label_width - new_size[0]) // 2
        y1 = (label_height - new_size[1]) // 2
        new_img.paste(resized_img, (x1, y1))

        img = ImageTk.PhotoImage(new_img)
        image_label.config(image=img)
        image_label.image = img  # keep a reference
        image_path = file_path
        save_data()
        update_image_label()


def create_entry(frame, placeholder, row, column, columnspan=1):
    entry = ttk.Entry(frame, font=ENTRY_FONT)
    entry.insert(0, placeholder)
    entry.bind("<FocusIn>", lambda event: on_entry_focus_in(event, placeholder))
    entry.bind("<FocusOut>", on_focus_out)
    entry.grid(
        row=row, column=column, padx=5, pady=5, columnspan=columnspan, sticky="ew"
    )
    return entry


def on_background_click(event):
    if not isinstance(event.widget, tk.Entry):
        root.focus_set()


def on_entry_focus_in(event, placeholder):
    entry = event.widget
    if entry.get() == placeholder:
        entry.delete(0, "end")


def on_focus_out(event):
    entry = event.widget
    placeholder = None
    for ph, ent in entries.items():
        if ent == entry:
            placeholder = ph
            break

    if placeholder is None:
        return

    if entry.get() == "":
        entry.insert(0, placeholder)
    else:
        save_data()
        update_image_label()


def save_data():
    user_data = {
        placeholder.lower(): entry.get() for placeholder, entry in entries.items()
    }
    user_data["image"] = f'images/letters/{user_data["last"][0].upper()}.jpg'
    if image_path is not None:
        user_data["image"] = image_path

    with open(DATA_FILE, "w") as file:
        json.dump(user_data, file)


def update_image_label():
    create_pdf()
    create_single_label()

    image = PhotoImage(file=SINGLE_LABEL_IMAGE_PATH)
    image_label.config(image=image)
    image_label.image = image


def create_label_sheet():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")]
    )
    if file_path:
        save_data()
        create_pdf(file_path)


# Run the application
if __name__ == "__main__":
    init_ui()
