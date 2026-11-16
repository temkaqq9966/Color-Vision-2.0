
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

        self.hue = 217 / 360
        self.saturation = 0.73
        self.value = 0.96

        self.area_width = 420
        self.area_height = 170

        self.hue_width = 420
        self.hue_height = 26
        self.hue_margin = 10

        self.rgb = (66, 135, 245)

        self.area_photo = None
        self.hue_photo = None

        self.build_ui()
        self.draw_color_area()
        self.draw_hue_slider()
        self.update_selected_color()

    def build_ui(self):

        # TITLE
        ctk.CTkLabel(
            self,
            text="CHOOSE YOUR COLOR",
            font=("Segoe UI", 16, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(12, 8)
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
        self.canvas.pack(padx=20)

        self.canvas.bind(
            "<Button-1>",
            self.select_color
        )

        self.canvas.bind(
            "<B1-Motion>",
            self.select_color
        )

        # HUE LABEL
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

        # RAINBOW HUE SLIDER
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

        # COLOR INFO
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

    # COLOR AREA
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

        # SELECTOR CIRCLE
        x = self.saturation * (width - 1)
        y = (1 - self.value) * (height - 1)

        self.canvas.create_oval(
            x - 7,
            y - 7,
            x + 7,
            y + 7,
            outline="#000000",
            width=4
        )

        self.canvas.create_oval(
            x - 7,
            y - 7,
            x + 7,
            y + 7,
            outline="#FFFFFF",
            width=2
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

        self.saturation = (
            x / (self.area_width - 1)
        )

        self.value = (
            1 - y / (self.area_height - 1)
        )

        self.update_selected_color()
        self.draw_color_area()

    # RAINBOW SLIDER
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

        # Draw full rainbow
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

        # Slider selector position
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

        track_width = (
            self.hue_width - margin * 2
        )

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

        self.draw_hue_slider()
        self.draw_color_area()
        self.update_selected_color()

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

    # UPDATE COLOR
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

        if self.command:
            self.command(self.rgb)

    # RESET
    def reset_color(self):
        self.hue = 217 / 360
        self.saturation = 0.73
        self.value = 0.96

        self.draw_hue_slider()
        self.draw_color_area()
        self.update_selected_color()

    def get_color(self):
        return self.rgb


