import os
import shutil
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
DESIRED_HEIGHT = 100
DESIRED_WIDTH = 300

# Global variables
root = ThemedTk(theme="plastik")
entries = {}
image_path = None
image_label = None


def init_ui():
    root.title(APP_TITLE)
    root.set_theme("plastik")
    root.iconbitmap(APP_ICON)
    root.geometry("600x400")
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
    img = Image.open(DEFAULT_IMAGE_PATH)
    photo_img = ImageTk.PhotoImage(img)
    image_label = tk.Label(root, image=photo_img, bg=APP_BG_COLOR)
    image_label.place(relx=0.65, rely=0.23, anchor="center")
    image_label.image = photo_img
    save_data()
    update_image_label()


def setup_input_frame():
    input_frame = tk.Frame(root, bg="#F4BFC3")
    input_frame.place(relx=0.5, rely=0.43, anchor="n", relwidth=0.9, relheight=0.6)

    for col in range(3):
        input_frame.grid_columnconfigure(col, weight=1)

    entry_configs = [
        (0, 0, 1),
        (0, 1, 3),
        (1, 0, 3),
        (2, 0, 1),
        (2, 1, 1),
        (2, 2, 1),
    ]

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

    button_id = create_rounded_rect(canvas, 10, 10, 190, 40, radius=10, fill='#F06A85')

    canvas.create_text(100, 25, text="Create", font=(FONT_NAME, 14), fill="white")

    canvas.create_rectangle(10, 10, 190, 40, outline="", fill="", tags="button_area")

    def on_click(event):
        create_label_sheet()

    canvas.tag_bind("button_area", "<Button-1>", on_click)
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

        if pil_img.mode != "RGBA":
            pil_img = pil_img.convert("RGBA")

        original_width, original_height = pil_img.size
        scaling_factor = 0.8

        new_width = int(original_width * scaling_factor)
        new_height = int(original_height * scaling_factor)

        resized_img = pil_img.resize((new_width, new_height), Image.LANCZOS)

        new_img = Image.new("RGBA", (DESIRED_WIDTH, DESIRED_HEIGHT),
                            (255, 255, 255, 255))

        x1 = (DESIRED_WIDTH - new_width) // 2
        y1 = (DESIRED_HEIGHT - new_height) // 2

        new_img.paste(resized_img, (x1, y1), resized_img)

        img = ImageTk.PhotoImage(new_img)
        image_label.image = img
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
    label_image = Image.open(SINGLE_LABEL_IMAGE_PATH)

    if label_image.mode != "RGBA":
        label_image = label_image.convert("RGBA")

    original_width, original_height = label_image.size
    ratio = min(DESIRED_WIDTH / original_width, DESIRED_HEIGHT / original_height)
    new_size = (int(original_width * ratio), int(original_height * ratio))

    new_img = Image.new("RGBA", (DESIRED_WIDTH, DESIRED_HEIGHT), (255, 255, 255, 0))

    x1 = (DESIRED_WIDTH - new_size[0]) // 2
    y1 = (DESIRED_HEIGHT - new_size[1]) // 2

    new_img.paste(label_image.resize(new_size, Image.Resampling.LANCZOS), (x1, y1))
    final_img = ImageTk.PhotoImage(new_img)
    image_label.config(image=final_img)
    image_label.image = final_img


def create_label_sheet():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile="labels.pdf"
    )
    if file_path:
        save_data()
        create_pdf(file_path)


# Run the application
if __name__ == "__main__":
    init_ui()
