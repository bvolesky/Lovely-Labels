import tkinter as tk
from tkinter import PhotoImage
import json
from create_pdf import create_pdf
from crop_pdf_to_single_label import create_single_label

# Constants
FONT_NAME = "Lato"
ENTRY_FONT = (FONT_NAME, 12)
DEFAULT_IMAGE_PATH = "output/default_single_address_label.png"
SINGLE_LABEL_IMAGE_PATH = "output/single_address_label.png"
DATA_FILE = "data/user_data.json"
APP_TITLE = "Lovely Labels"
APP_ICON = "images/ll_transparent.ico"
APP_BG_COLOR = "#FEE6DE"
PLACEHOLDERS = ["First", "Last", "Address", "City", "State", "Zip"]

# Global variables
root = tk.Tk()
entries = {}
image_label = None


def init_ui():
    root.title(APP_TITLE)
    root.iconbitmap(APP_ICON)
    root.geometry("400x300")
    root.configure(bg=APP_BG_COLOR)
    root.bind("<Button-1>", on_background_click)

    setup_input_frame()
    setup_default_image()

    root.mainloop()


def setup_input_frame():
    # Create a frame for the input fields
    input_frame = tk.Frame(root, bg="#FEE6DE")
    input_frame.place(relx=0.5, rely=0.4, anchor="n", relwidth=0.7, relheight=0.33)

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



def setup_default_image():
    global image_label
    image = PhotoImage(file=DEFAULT_IMAGE_PATH)
    image_label = tk.Label(root, image=image, bg=APP_BG_COLOR)
    image_label.place(relx=0.5, rely=0.2, anchor="center")
    image_label.image = image


def create_entry(frame, placeholder, row, column, columnspan=1):
    entry = tk.Entry(frame, font=ENTRY_FONT, fg="grey")
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
        entry.config(fg="black")


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
        entry.config(fg="grey")
    else:
        save_data()
        update_image_label()


def save_data():
    user_data = {
        placeholder.lower(): entry.get() for placeholder, entry in entries.items()
    }
    user_data["image"] = f'images/letters/{user_data["last"][0].upper()}.jpg'

    with open(DATA_FILE, "w") as file:
        json.dump(user_data, file)


def update_image_label():
    create_pdf()
    create_single_label()

    image = PhotoImage(file=SINGLE_LABEL_IMAGE_PATH)
    image_label.config(image=image)
    image_label.image = image


# Run the application
if __name__ == "__main__":
    init_ui()
