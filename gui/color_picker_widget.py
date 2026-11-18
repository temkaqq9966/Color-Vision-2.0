
import colorsys
import re
import tkinter as tk

import customtkinter as ctk


class ColorPickerWidget(ctk.CTkFrame):

    def __init__(
        self,
        master,
        command=None,
        show_finders=True
    ):
        super().__init__(
            master,
            fg_color="#171C2A",
            corner_radius=14
        )

        self.command = command
        self.show_finders = show_finders

        self.default_rgb = (66, 135, 245)
        self.rgb = self.default_rgb

        self.hue = 0.0
        self.saturation = 0.0
        self.value = 1.0

        self.area_width = 420
        self.area_height = 170
        self.hue_width = 420
        self.hue_height = 24

        self.active_section = None
        self.sections = {}
        self.section_buttons = {}

        self.area_photo = None
        self.hue_photo = None

        self.build_ui()
        self.set_rgb(*self.default_rgb)

    # =====================================
    # USER INTERFACE
    # =====================================
    def build_ui(self):

        ctk.CTkLabel(
            self,
            text="CHOOSE YOUR COLOR",
            font=("Segoe UI", 17, "bold")
        ).pack(
            anchor="w",
            padx=14,
            pady=(15, 14)
        )

        # Finder-үүдийг зөвхөн шаардлагатай
        # хуудсанд үүсгэнэ.
        if self.show_finders:

            ctk.CTkLabel(
                self,
                text="COLOR FINDERS",
                font=("Segoe UI", 12, "bold"),
                text_color="#94A3B8"
            ).pack(
                anchor="w",
                padx=14,
                pady=(0, 8)
            )

            self.create_rgb_section()
            self.create_hex_section()
            self.create_hsv_section()

        self.error_label = ctk.CTkLabel(
            self,
            text="",
            text_color="#F87171",
            font=("Segoe UI", 12)
        )

        if self.show_finders:
            self.error_label.pack(pady=(0, 5))

        # COLOR AREA
        self.area_canvas = tk.Canvas(
            self,
            width=self.area_width,
            height=self.area_height,
            bg="#111827",
            highlightthickness=0,
            bd=0,
            cursor="crosshair"
        )
        self.area_canvas.pack(
            padx=14,
            pady=(12, 10)
        )

        self.area_canvas.bind(
            "<Button-1>",
            self.select_color
        )
        self.area_canvas.bind(
            "<B1-Motion>",
            self.select_color
        )

        hue_header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        hue_header.pack(
            fill="x",
            padx=14,
            pady=(8, 4)
        )

        ctk.CTkLabel(
            hue_header,
            text="HUE",
            font=("Segoe UI", 12),
            text_color="#94A3B8"
        ).pack(side="left")

        self.hue_label = ctk.CTkLabel(
            hue_header,
            text="0°",
            font=("Segoe UI", 12, "bold")
        )
        self.hue_label.pack(side="right")

        self.hue_canvas = tk.Canvas(
            self,
            width=self.hue_width,
            height=self.hue_height,
            bg="#111827",
            highlightthickness=0,
            bd=0,
            cursor="hand2"
        )
        self.hue_canvas.pack(
            padx=14,
            pady=(0, 14)
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
        preview_row = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        preview_row.pack(
            fill="x",
            padx=14,
            pady=(0, 15)
        )

        self.preview = ctk.CTkFrame(
            preview_row,
            width=65,
            height=55,
            fg_color="#4287F5",
            corner_radius=10
        )
        self.preview.pack(side="left")
        self.preview.pack_propagate(False)

        info = ctk.CTkFrame(
            preview_row,
            fg_color="transparent"
        )
        info.pack(
            side="left",
            padx=14
        )

        self.hex_label = ctk.CTkLabel(
            info,
            text="#4287F5",
            font=("Consolas", 16, "bold")
        )
        self.hex_label.pack(anchor="w")

        self.rgb_label = ctk.CTkLabel(
            info,
            text="RGB: 66, 135, 245",
            font=("Consolas", 12),
            text_color="#94A3B8"
        )
        self.rgb_label.pack(anchor="w")

    # =====================================
    # COLLAPSIBLE SECTIONS
    # =====================================
    def create_section(self, name):

        wrapper = ctk.CTkFrame(
            self,
            fg_color="#20283A",
            corner_radius=7
        )
        wrapper.pack(
            fill="x",
            padx=14,
            pady=4
        )

        button = ctk.CTkButton(
            wrapper,
            text=f"▶ {name} COLOR FINDER",
            height=40,
            anchor="w",
            fg_color="#20283A",
            hover_color="#2D3B55",
            command=lambda n=name:
                self.toggle_section(n)
        )
        button.pack(fill="x")

        content = ctk.CTkFrame(
            wrapper,
            fg_color="#20283A"
        )

        self.sections[name] = content
        self.section_buttons[name] = button

        return content

    def toggle_section(self, name):

        if self.active_section == name:

            self.sections[name].pack_forget()
            self.section_buttons[name].configure(
                text=f"▶ {name} COLOR FINDER"
            )
            self.active_section = None
            return

        for section_name, content in self.sections.items():

            content.pack_forget()

            self.section_buttons[
                section_name
            ].configure(
                text=f"▶ {section_name} COLOR FINDER"
            )

        self.sections[name].pack(
            fill="x",
            padx=10,
            pady=(0, 10)
        )

        self.section_buttons[name].configure(
            text=f"▼ {name} COLOR FINDER"
        )

        self.active_section = name

    # =====================================
    # RGB FINDER
    # =====================================
    def create_rgb_section(self):

        content = self.create_section("RGB")

        row = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )
        row.pack(
            fill="x",
            padx=5,
            pady=5
        )

        self.rgb_entries = []

        for label in ("R", "G", "B"):

            column = ctk.CTkFrame(
                row,
                fg_color="transparent"
            )
            column.pack(
                side="left",
                fill="x",
                expand=True,
                padx=3
            )

            ctk.CTkLabel(
                column,
                text=label
            ).pack()

            entry = ctk.CTkEntry(
                column,
                width=75,
                justify="center"
            )
            entry.pack(fill="x")

            self.rgb_entries.append(entry)

        ctk.CTkButton(
            content,
            text="Apply RGB",
            command=self.apply_rgb
        ).pack(
            fill="x",
            padx=8,
            pady=8
        )

    def apply_rgb(self):

        try:
            values = [
                int(entry.get().strip())
                for entry in self.rgb_entries
            ]

            if any(
                value < 0 or value > 255
                for value in values
            ):
                raise ValueError

            self.set_rgb(*values)
            self.show_error("")

        except ValueError:
            self.show_error(
                "RGB values must be 0–255."
            )

    # =====================================
    # HEX FINDER
    # =====================================
    def create_hex_section(self):

        content = self.create_section("HEX")

        self.hex_entry = ctk.CTkEntry(
            content,
            placeholder_text="#4287F5"
        )
        self.hex_entry.pack(
            fill="x",
            padx=8,
            pady=(8, 5)
        )

        ctk.CTkButton(
            content,
            text="Apply HEX",
            command=self.apply_hex
        ).pack(
            fill="x",
            padx=8,
            pady=(0, 8)
        )

    def apply_hex(self):

        value = self.hex_entry.get().strip()

        if not re.fullmatch(
            r"#?[0-9A-Fa-f]{6}",
            value
        ):
            self.show_error(
                "Invalid HEX. Example: #4287F5"
            )
            return

        value = value.lstrip("#")

        rgb = tuple(
            int(value[i:i + 2], 16)
            for i in (0, 2, 4)
        )

        self.set_rgb(*rgb)
        self.show_error("")

    # =====================================
    # HSV FINDER
    # =====================================
    def create_hsv_section(self):

        content = self.create_section("HSV")

        row = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )
        row.pack(
            fill="x",
            padx=5,
            pady=5
        )

        self.hsv_entries = []

        for label in ("H", "S", "V"):

            column = ctk.CTkFrame(
                row,
                fg_color="transparent"
            )
            column.pack(
                side="left",
                fill="x",
                expand=True,
                padx=3
            )

            ctk.CTkLabel(
                column,
                text=label
            ).pack()

            entry = ctk.CTkEntry(
                column,
                width=75,
                justify="center"
            )
            entry.pack(fill="x")

            self.hsv_entries.append(entry)

        ctk.CTkButton(
            content,
            text="Apply HSV",
            command=self.apply_hsv
        ).pack(
            fill="x",
            padx=8,
            pady=8
        )

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

            self.hue = (h % 360) / 360
            self.saturation = s / 100
            self.value = v / 100

            self.refresh_color()
            self.show_error("")

        except ValueError:
            self.show_error(
                "HSV ranges: H 0–360, S/V 0–100."
            )

    def show_error(self, message):

        if self.show_finders:
            self.error_label.configure(
                text=message
            )

    # =====================================
    # COLOR CONVERSION
    # =====================================
    def set_rgb(self, *args):

        if len(args) == 1:
            rgb = args[0]
        else:
            rgb = args

        if len(rgb) != 3:
            raise ValueError(
                "RGB must contain 3 values."
            )

        r, g, b = (
            int(value)
            for value in rgb
        )

        if any(
            value < 0 or value > 255
            for value in (r, g, b)
        ):
            raise ValueError(
                "RGB values must be 0–255."
            )

        self.hue, self.saturation, self.value = (
            colorsys.rgb_to_hsv(
                r / 255,
                g / 255,
                b / 255
            )
        )

        self.refresh_color()

    def refresh_color(self):

        self.update_selected_color()
        self.draw_color_area()
        self.draw_hue_slider()

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

        hex_value = "#{:02X}{:02X}{:02X}".format(
            *self.rgb
        )

        self.preview.configure(
            fg_color=hex_value
        )

        self.hex_label.configure(
            text=hex_value
        )

        self.rgb_label.configure(
            text=(
                f"RGB: {self.rgb[0]}, "
                f"{self.rgb[1]}, {self.rgb[2]}"
            )
        )

        self.hue_label.configure(
            text=f"{round(self.hue * 360)}°"
        )

        if self.show_finders:

            hsv_values = (
                round(self.hue * 360),
                round(self.saturation * 100),
                round(self.value * 100)
            )

            for entry, value in zip(
                self.rgb_entries,
                self.rgb
            ):
                self.update_entry(entry, str(value))

            self.update_entry(
                self.hex_entry,
                hex_value
            )

            for entry, value in zip(
                self.hsv_entries,
                hsv_values
            ):
                self.update_entry(entry, str(value))

        if self.command is not None:
            self.command(self.rgb)

    def update_entry(self, entry, value):

        if entry.focus_get() == entry:
            return

        entry.delete(0, "end")
        entry.insert(0, value)

    # =====================================
    # COLOR AREA
    # =====================================
    def draw_color_area(self):

        width = self.area_width
        height = self.area_height

        image = tk.PhotoImage(
            width=width,
            height=height
        )

        for y in range(height):

            value = 1 - y / max(1, height - 1)
            pixels = []

            for x in range(width):

                saturation = x / max(1, width - 1)

                r, g, b = colorsys.hsv_to_rgb(
                    self.hue,
                    saturation,
                    value
                )

                pixels.append(
                    "#{:02x}{:02x}{:02x}".format(
                        round(r * 255),
                        round(g * 255),
                        round(b * 255)
                    )
                )

            image.put(
                "{" + " ".join(pixels) + "}",
                to=(0, y)
            )

        self.area_photo = image

        self.area_canvas.delete("all")

        self.area_canvas.create_image(
            0,
            0,
            anchor="nw",
            image=self.area_photo
        )

        x = round(
            self.saturation * (width - 1)
        )
        y = round(
            (1 - self.value) * (height - 1)
        )

        self.area_canvas.create_oval(
            x - 4,
            y - 4,
            x + 4,
            y + 4,
            outline="white",
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
            x / max(1, self.area_width - 1)
        )
        self.value = (
            1 - y / max(1, self.area_height - 1)
        )

        self.update_selected_color()

        # Зөвхөн сонгогчийн тэмдэглэгээг шинэчилнэ.
        self.area_canvas.delete("selector")

        self.area_canvas.create_oval(
            x - 4,
            y - 4,
            x + 4,
            y + 4,
            outline="white",
            width=2,
            tags="selector"
        )

    # =====================================
    # HUE SLIDER
    # =====================================
    def draw_hue_slider(self):

        image = tk.PhotoImage(
            width=self.hue_width,
            height=self.hue_height
        )

        for x in range(self.hue_width):

            hue = x / max(1, self.hue_width - 1)

            r, g, b = colorsys.hsv_to_rgb(
                hue,
                1,
                1
            )

            color = "#{:02x}{:02x}{:02x}".format(
                round(r * 255),
                round(g * 255),
                round(b * 255)
            )

            image.put(
                color,
                to=(x, 0, x + 1, self.hue_height)
            )

        self.hue_photo = image

        self.hue_canvas.delete("all")

        self.hue_canvas.create_image(
            0,
            0,
            anchor="nw",
            image=self.hue_photo
        )

        x = round(
            self.hue * (self.hue_width - 1)
        )

        self.hue_canvas.create_oval(
            x - 5,
            self.hue_height // 2 - 5,
            x + 5,
            self.hue_height // 2 + 5,
            fill="#FFFFFF",
            outline="#111827",
            width=2
        )

    def select_hue(self, event):

        x = max(
            0,
            min(event.x, self.hue_width - 1)
        )

        self.hue = x / max(
            1,
            self.hue_width - 1
        )

        self.refresh_color()

    # =====================================
    # PUBLIC METHODS
    # =====================================
    def get_color(self):
        return self.rgb

    def reset_color(self):
        self.set_rgb(*self.default_rgb)


# =========================================
# STANDALONE TEST
# =========================================
if __name__ == "__main__":

    ctk.set_appearance_mode("dark")

    app = ctk.CTk()
    app.title("ColorVision 2.0 - Color Picker")
    app.geometry("550x760")

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
