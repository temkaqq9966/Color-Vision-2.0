
import colorsys
import tkinter as tk

import customtkinter as ctk
from PIL import Image, ImageTk


class ColorPickerWidget(ctk.CTkFrame):

    def __init__(self, master, command=None):
        super().__init__(
            master,
            fg_color="#171C2A",
            corner_radius=16
        )

        self.command = command

        self.default_rgb = (66, 135, 245)

        self.hue = 217 / 360
        self.saturation = 0.73
        self.value = 0.96
        self.rgb = self.default_rgb

        self.area_width = 420
        self.area_height = 170

        self.hue_width = 420
        self.hue_height = 26
        self.hue_margin = 10

        self.area_photo = None
        self.hue_photo = None

        self.sections = {}
        self.section_buttons = {}
        self.active_section = None

        self.build_ui()
        self.set_rgb(*self.default_rgb)

    # =====================================
    # MAIN UI
    # =====================================
    def build_ui(self):

        ctk.CTkLabel(
            self,
            text="CHOOSE YOUR COLOR",
            font=("Segoe UI", 16, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(12, 8)
        )

        # FINDERS - өнгөний талбайн ДЭЭР
        ctk.CTkLabel(
            self,
            text="COLOR FINDERS",
            font=("Segoe UI", 12, "bold"),
            text_color="#94A3B8"
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 6)
        )

        self.create_rgb_section()
        self.create_hex_section()
        self.create_hsv_section()

        self.error_label = ctk.CTkLabel(
            self,
            text="",
            height=18,
            font=("Segoe UI", 11),
            text_color="#F87171"
        )
        self.error_label.pack(
            fill="x",
            padx=20,
            pady=(2, 4)
        )

        # COLOR AREA
        self.canvas = tk.Canvas(
            self,
            width=self.area_width,
            height=self.area_height,
            highlightthickness=0,
            bd=0,
            cursor="crosshair"
        )
        self.canvas.pack(padx=20, pady=(5, 0))

        self.canvas.bind(
            "<Button-1>",
            self.select_color
        )
        self.canvas.bind(
            "<B1-Motion>",
            self.select_color
        )

        # HUE HEADER
        hue_header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        hue_header.pack(
            fill="x",
            padx=20,
            pady=(10, 3)
        )

        ctk.CTkLabel(
            hue_header,
            text="HUE",
            font=("Segoe UI", 11),
            text_color="#94A3B8"
        ).pack(side="left")

        self.hue_value_label = ctk.CTkLabel(
            hue_header,
            text="217°",
            font=("Segoe UI", 11, "bold"),
            text_color="#CBD5E1"
        )
        self.hue_value_label.pack(side="right")

        # HUE SLIDER
        self.hue_canvas = tk.Canvas(
            self,
            width=self.hue_width,
            height=self.hue_height,
            highlightthickness=0,
            bd=0,
            bg="#171C2A",
            cursor="hand2"
        )
        self.hue_canvas.pack(
            padx=20,
            pady=(0, 10)
        )

        self.hue_canvas.bind(
            "<Button-1>",
            self.select_hue
        )
        self.hue_canvas.bind(
            "<B1-Motion>",
            self.select_hue
        )

        # PREVIEW
        info = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        info.pack(
            fill="x",
            padx=20,
            pady=(0, 12)
        )

        self.preview = ctk.CTkFrame(
            info,
            width=55,
            height=45,
            corner_radius=9,
            fg_color="#4287F5"
        )
        self.preview.pack(side="left")
        self.preview.pack_propagate(False)

        self.hex_label = ctk.CTkLabel(
            info,
            text="#4287F5",
            font=("Consolas", 16, "bold")
        )
        self.hex_label.pack(
            side="left",
            padx=15
        )

        self.rgb_label = ctk.CTkLabel(
            info,
            text="RGB: 66, 135, 245",
            text_color="#94A3B8"
        )
        self.rgb_label.pack(side="right")

    # =====================================
    # COLLAPSIBLE SECTIONS
    # =====================================
    def create_section(self, name):

        wrapper = ctk.CTkFrame(
            self,
            fg_color="#202738",
            corner_radius=10
        )
        wrapper.pack(
            fill="x",
            padx=20,
            pady=4
        )

        button = ctk.CTkButton(
            wrapper,
            text=f"▶  {name} COLOR FINDER",
            anchor="w",
            height=40,
            fg_color="transparent",
            hover_color="#303B54",
            font=("Segoe UI", 12, "bold"),
            command=lambda: self.toggle_section(name)
        )
        button.pack(fill="x")

        content = ctk.CTkFrame(
            wrapper,
            fg_color="transparent"
        )

        self.sections[name] = content
        self.section_buttons[name] = button

        return content

    def toggle_section(self, name):

        if self.active_section == name:

            self.sections[name].pack_forget()

            self.section_buttons[name].configure(
                text=f"▶  {name} COLOR FINDER"
            )

            self.active_section = None
            return

        if self.active_section is not None:

            old = self.active_section

            self.sections[old].pack_forget()

            self.section_buttons[old].configure(
                text=f"▶  {old} COLOR FINDER"
            )

        self.sections[name].pack(
            fill="x",
            padx=12,
            pady=(0, 12)
        )

        self.section_buttons[name].configure(
            text=f"▼  {name} COLOR FINDER"
        )

        self.active_section = name

    # =====================================
    # RGB FINDER
    # =====================================
    def create_rgb_section(self):

        content = self.create_section("RGB")

        ctk.CTkLabel(
            content,
            text="Enter RGB values (0 - 255)",
            text_color="#94A3B8"
        ).pack(anchor="w", pady=(0, 8))

        row = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )
        row.pack(fill="x")

        self.rgb_entries = []

        for label in ("R", "G", "B"):

            column = ctk.CTkFrame(
                row,
                fg_color="transparent"
            )
            column.pack(
                side="left",
                expand=True,
                fill="x",
                padx=3
            )

            ctk.CTkLabel(
                column,
                text=label
            ).pack()

            entry = ctk.CTkEntry(
                column,
                width=90,
                height=34,
                justify="center"
            )
            entry.pack(fill="x")

            entry.bind(
                "<Return>",
                lambda event: self.apply_rgb()
            )

            self.rgb_entries.append(entry)

        ctk.CTkButton(
            content,
            text="FIND RGB COLOR",
            height=36,
            command=self.apply_rgb
        ).pack(fill="x", pady=(12, 0))

    def apply_rgb(self):

        try:
            values = [
                int(entry.get().strip())
                for entry in self.rgb_entries
            ]

            if not all(0 <= v <= 255 for v in values):
                raise ValueError

        except ValueError:
            self.show_error(
                "RGB must contain integers from 0 to 255."
            )
            return

        self.set_rgb(*values)

    # =====================================
    # HEX FINDER
    # =====================================
    def create_hex_section(self):

        content = self.create_section("HEX")

        ctk.CTkLabel(
            content,
            text="Enter HEX color code",
            text_color="#94A3B8"
        ).pack(anchor="w", pady=(0, 8))

        self.hex_entry = ctk.CTkEntry(
            content,
            height=38,
            placeholder_text="#FF5733",
            font=("Consolas", 14)
        )
        self.hex_entry.pack(fill="x")

        self.hex_entry.bind(
            "<Return>",
            lambda event: self.apply_hex()
        )

        ctk.CTkButton(
            content,
            text="FIND HEX COLOR",
            height=36,
            command=self.apply_hex
        ).pack(fill="x", pady=(12, 0))

    def apply_hex(self):

        code = self.hex_entry.get().strip()

        if code.startswith("#"):
            code = code[1:]

        if (
            len(code) != 6
            or any(
                char not in "0123456789abcdefABCDEF"
                for char in code
            )
        ):
            self.show_error(
                "Enter a valid HEX code, e.g. #FF5733."
            )
            return

        r = int(code[0:2], 16)
        g = int(code[2:4], 16)
        b = int(code[4:6], 16)

        self.set_rgb(r, g, b)

    # =====================================
    # HSV FINDER
    # =====================================
    def create_hsv_section(self):

        content = self.create_section("HSV")

        ctk.CTkLabel(
            content,
            text="H: 0-360 | S: 0-100 | V: 0-100",
            text_color="#94A3B8"
        ).pack(anchor="w", pady=(0, 8))

        row = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )
        row.pack(fill="x")

        self.hsv_entries = []

        for label in ("H", "S", "V"):

            column = ctk.CTkFrame(
                row,
                fg_color="transparent"
            )
            column.pack(
                side="left",
                expand=True,
                fill="x",
                padx=3
            )

            ctk.CTkLabel(
                column,
                text=label
            ).pack()

            entry = ctk.CTkEntry(
                column,
                width=90,
                height=34,
                justify="center"
            )
            entry.pack(fill="x")

            entry.bind(
                "<Return>",
                lambda event: self.apply_hsv()
            )

            self.hsv_entries.append(entry)

        ctk.CTkButton(
            content,
            text="FIND HSV COLOR",
            height=36,
            command=self.apply_hsv
        ).pack(fill="x", pady=(12, 0))

    def apply_hsv(self):

        try:
            h, s, v = [
                float(entry.get().strip())
                for entry in self.hsv_entries
            ]

            if not (
                0 <= h <= 360
                and 0 <= s <= 100
                and 0 <= v <= 100
            ):
                raise ValueError

        except ValueError:
            self.show_error(
                "HSV: H 0-360, S 0-100, V 0-100."
            )
            return

        self.hue = (h % 360) / 360
        self.saturation = s / 100
        self.value = v / 100

        self.refresh_color(redraw_area=True)

    # =====================================
    # SET RGB
    # =====================================
    def set_rgb(self, r, g, b):

        h, s, v = colorsys.rgb_to_hsv(
            r / 255,
            g / 255,
            b / 255
        )

        self.hue = h
        self.saturation = s
        self.value = v

        self.refresh_color(redraw_area=True)

    def refresh_color(self, redraw_area=False):

        if redraw_area:
            self.draw_color_area()
        else:
            self.draw_selector()

        self.draw_hue_slider()
        self.update_selected_color()

    def show_error(self, message):
        self.error_label.configure(text=message)

    def clear_error(self):
        self.error_label.configure(text="")

    # =====================================
    # COLOR AREA
    # =====================================
    def draw_color_area(self):

        width = self.area_width
        height = self.area_height

        image = Image.new(
            "RGB",
            (width, height)
        )
        pixels = image.load()

        for y in range(height):

            v = 1 - y / (height - 1)

            for x in range(width):

                s = x / (width - 1)

                r, g, b = colorsys.hsv_to_rgb(
                    self.hue,
                    s,
                    v
                )

                pixels[x, y] = (
                    round(r * 255),
                    round(g * 255),
                    round(b * 255)
                )

        self.area_photo = ImageTk.PhotoImage(image)

        self.canvas.delete("all")

        self.canvas.create_image(
            0,
            0,
            anchor="nw",
            image=self.area_photo
        )

        self.draw_selector()

    def draw_selector(self):

        self.canvas.delete("selector")

        x = self.saturation * (self.area_width - 1)
        y = (1 - self.value) * (self.area_height - 1)

        self.canvas.create_oval(
            x - 7,
            y - 7,
            x + 7,
            y + 7,
            outline="#000000",
            width=4,
            tags="selector"
        )

        self.canvas.create_oval(
            x - 7,
            y - 7,
            x + 7,
            y + 7,
            outline="#FFFFFF",
            width=2,
            tags="selector"
        )

    def select_color(self, event):

        x = max(
            0,
            min(event.x, self.area_width - 1)
        )

        y = max(
            0,
            min(event.y, self.area_height - 1)
        )

        self.saturation = x / (self.area_width - 1)
        self.value = 1 - y / (self.area_height - 1)

        self.refresh_color(redraw_area=False)

    # =====================================
    # HUE SLIDER
    # =====================================
    def draw_hue_slider(self):

        width = self.hue_width
        height = self.hue_height
        margin = self.hue_margin

        track_width = width - margin * 2

        image = Image.new(
            "RGB",
            (width, height),
            "#171C2A"
        )
        pixels = image.load()

        for x in range(margin, width - margin):

            hue = (
                (x - margin)
                / max(1, track_width - 1)
            )

            r, g, b = colorsys.hsv_to_rgb(
                hue,
                1,
                1
            )

            color = (
                round(r * 255),
                round(g * 255),
                round(b * 255)
            )

            for y in range(8, height - 8):
                pixels[x, y] = color

        self.hue_photo = ImageTk.PhotoImage(image)

        self.hue_canvas.delete("all")

        self.hue_canvas.create_image(
            0,
            0,
            anchor="nw",
            image=self.hue_photo
        )

        selector_x = (
            margin + self.hue * (track_width - 1)
        )
        selector_y = height / 2

        self.hue_canvas.create_oval(
            selector_x - 9,
            selector_y - 9,
            selector_x + 9,
            selector_y + 9,
            fill="#111827",
            outline="#111827",
            width=2
        )

        self.hue_canvas.create_oval(
            selector_x - 7,
            selector_y - 7,
            selector_x + 7,
            selector_y + 7,
            fill=self.hue_to_hex(),
            outline="#FFFFFF",
            width=3
        )

        self.hue_value_label.configure(
            text=f"{round(self.hue * 360)}°"
        )

    def select_hue(self, event):

        margin = self.hue_margin
        track_width = self.hue_width - margin * 2

        x = max(
            margin,
            min(
                event.x,
                self.hue_width - margin - 1
            )
        )

        self.hue = (
            (x - margin)
            / max(1, track_width - 1)
        )

        self.refresh_color(redraw_area=True)

    def hue_to_hex(self):

        r, g, b = colorsys.hsv_to_rgb(
            self.hue,
            1,
            1
        )

        return "#{:02X}{:02X}{:02X}".format(
            round(r * 255),
            round(g * 255),
            round(b * 255)
        )

    # =====================================
    # UPDATE SELECTED COLOR
    # =====================================
    def update_selected_color(self):

        r, g, b = colorsys.hsv_to_rgb(
            self.hue,
            self.saturation,
            self.value
        )

        self.rgb = (
            round(r * 255),
            round(g * 255),
            round(b * 255)
        )

        hex_color = "#{:02X}{:02X}{:02X}".format(
            *self.rgb
        )

        self.preview.configure(
            fg_color=hex_color
        )

        self.hex_label.configure(
            text=hex_color
        )

        self.rgb_label.configure(
            text=(
                f"RGB: {self.rgb[0]}, "
                f"{self.rgb[1]}, {self.rgb[2]}"
            )
        )

        for entry, value in zip(
            self.rgb_entries,
            self.rgb
        ):
            self.update_entry(entry, str(value))

        self.update_entry(
            self.hex_entry,
            hex_color
        )

        hsv_values = (
            round(self.hue * 360),
            round(self.saturation * 100, 1),
            round(self.value * 100, 1)
        )

        for entry, value in zip(
            self.hsv_entries,
            hsv_values
        ):
            self.update_entry(entry, str(value))

        self.clear_error()

        if self.command:
            self.command(self.rgb)

    def update_entry(self, entry, value):

        if entry.focus_get() == entry:
            return

        entry.delete(0, "end")
        entry.insert(0, value)

    # =====================================
    # RESET / GET COLOR
    # =====================================
    def reset_color(self):
        self.set_rgb(*self.default_rgb)

    def get_color(self):
        return self.rgb


# =========================================
# ТУСАД НЬ ТУРШИХ
# =========================================
if __name__ == "__main__":

    ctk.set_appearance_mode("dark")

    app = ctk.CTk()
    app.title("ColorVision 2.0 - Color Picker")
    app.geometry("550x760")

    # Scroll ашигласнаар доод хэсэг
    # дэлгэцээс тасрахгүй.
    scroll = ctk.CTkScrollableFrame(
        app,
        fg_color="transparent"
    )
    scroll.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=15
    )

    picker = ColorPickerWidget(scroll)
    picker.pack(fill="x")

    app.mainloop()
