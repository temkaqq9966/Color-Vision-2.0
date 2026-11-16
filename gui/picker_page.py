
import colorsys
import re
import customtkinter as ctk

from core.color_matcher import (
    load_colors,
    save_colors,
    add_custom_color
)


class PickerPage(ctk.CTkFrame):
    def __init__(self, master, go_back):
        super().__init__(master, fg_color="#090B12")

        self.go_back = go_back
        self.updating = False

        self.hue = 0
        self.saturation = 100
        self.brightness = 100

        self.build_ui()
        self.update_color()
        self.refresh_saved_colors()

    def build_ui(self):
        header = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        header.pack(
            fill="x", padx=25, pady=(20, 12)
        )

        ctk.CTkButton(
            header,
            text="← Dashboard",
            width=130,
            fg_color="#252B3A",
            command=self.go_back
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text="COLOR PICKER",
            font=("Segoe UI", 26, "bold")
        ).pack(side="left", padx=25)

        content = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        content.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(5, 20)
        )

        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)

        left = ctk.CTkScrollableFrame(
            content,
            fg_color="#171C2A",
            corner_radius=18
        )
        left.grid(
            row=0, column=0,
            sticky="nsew",
            padx=(0, 10)
        )

        ctk.CTkLabel(
            left,
            text="CREATE YOUR COLOR",
            font=("Segoe UI", 17, "bold")
        ).pack(
            anchor="w", padx=20, pady=(20, 12)
        )

        self.preview = ctk.CTkFrame(
            left,
            height=125,
            corner_radius=14,
            fg_color="#FF0000"
        )
        self.preview.pack(
            fill="x", padx=20, pady=(0, 20)
        )
        self.preview.pack_propagate(False)

        self.hue_label = ctk.CTkLabel(
            left, text="Hue: 0°"
        )
        self.hue_label.pack(
            anchor="w", padx=20
        )

        self.hue_slider = ctk.CTkSlider(
            left,
            from_=0,
            to=360,
            number_of_steps=360,
            command=self.change_hue
        )
        self.hue_slider.pack(
            fill="x", padx=20, pady=(5, 18)
        )
        self.hue_slider.set(0)

        self.saturation_label = ctk.CTkLabel(
            left, text="Saturation: 100%"
        )
        self.saturation_label.pack(
            anchor="w", padx=20
        )

        self.saturation_slider = ctk.CTkSlider(
            left,
            from_=0,
            to=100,
            number_of_steps=100,
            command=self.change_saturation
        )
        self.saturation_slider.pack(
            fill="x", padx=20, pady=(5, 18)
        )
        self.saturation_slider.set(100)

        self.brightness_label = ctk.CTkLabel(
            left, text="Brightness: 100%"
        )
        self.brightness_label.pack(
            anchor="w", padx=20
        )

        self.brightness_slider = ctk.CTkSlider(
            left,
            from_=0,
            to=100,
            number_of_steps=100,
            command=self.change_brightness
        )
        self.brightness_slider.pack(
            fill="x", padx=20, pady=(5, 18)
        )
        self.brightness_slider.set(100)

        self.hex_label = ctk.CTkLabel(
            left,
            text="HEX: #FF0000",
            font=("Consolas", 17, "bold")
        )
        self.hex_label.pack(pady=(8, 4))

        self.rgb_label = ctk.CTkLabel(
            left,
            text="RGB: 255, 0, 0",
            font=("Consolas", 15)
        )
        self.rgb_label.pack(pady=4)

        ctk.CTkLabel(
            left,
            text="ENTER HEX COLOR",
            font=("Segoe UI", 13, "bold")
        ).pack(pady=(18, 6))

        self.hex_entry = ctk.CTkEntry(
            left,
            placeholder_text="#AABBCC",
            height=38
        )
        self.hex_entry.pack(
            fill="x", padx=20
        )

        ctk.CTkButton(
            left,
            text="Apply HEX",
            height=38,
            command=self.apply_hex
        ).pack(
            fill="x", padx=20, pady=(8, 20)
        )

        # RIGHT PANEL
        right = ctk.CTkScrollableFrame(
            content,
            fg_color="#171C2A",
            corner_radius=18
        )
        right.grid(
            row=0, column=1, sticky="nsew"
        )

        ctk.CTkLabel(
            right,
            text="SAVE COLOR",
            font=("Segoe UI", 17, "bold")
        ).pack(
            anchor="w", padx=18, pady=(20, 12)
        )

        self.name_entry = ctk.CTkEntry(
            right,
            placeholder_text="Color name",
            height=40
        )
        self.name_entry.pack(
            fill="x", padx=18
        )

        ctk.CTkButton(
            right,
            text="Save Color",
            height=40,
            fg_color="#16A34A",
            hover_color="#15803D",
            command=self.save_color
        ).pack(
            fill="x", padx=18, pady=10
        )

        self.message_label = ctk.CTkLabel(
            right,
            text="",
            text_color="#4ADE80",
            wraplength=250
        )
        self.message_label.pack(pady=5)

        ctk.CTkLabel(
            right,
            text="SAVED COLORS",
            font=("Segoe UI", 17, "bold")
        ).pack(
            anchor="w", padx=18, pady=(15, 10)
        )

        self.saved_container = ctk.CTkFrame(
            right,
            fg_color="transparent"
        )
        self.saved_container.pack(
            fill="x", padx=15, pady=(0, 15)
        )

    def change_hue(self, value):
        if self.updating:
            return
        self.hue = int(value)
        self.update_color()

    def change_saturation(self, value):
        if self.updating:
            return
        self.saturation = int(value)
        self.update_color()

    def change_brightness(self, value):
        if self.updating:
            return
        self.brightness = int(value)
        self.update_color()

    def update_color(self):
        r, g, b = colorsys.hsv_to_rgb(
            self.hue / 360,
            self.saturation / 100,
            self.brightness / 100
        )

        self.rgb = (
            round(r * 255),
            round(g * 255),
            round(b * 255)
        )

        self.hex_color = "#{:02X}{:02X}{:02X}".format(
            *self.rgb
        )

        self.preview.configure(
            fg_color=self.hex_color
        )

        self.hue_label.configure(
            text=f"Hue: {self.hue}°"
        )
        self.saturation_label.configure(
            text=f"Saturation: {self.saturation}%"
        )
        self.brightness_label.configure(
            text=f"Brightness: {self.brightness}%"
        )

        self.hex_label.configure(
            text=f"HEX: {self.hex_color}"
        )
        self.rgb_label.configure(
            text=f"RGB: {self.rgb[0]}, {self.rgb[1]}, {self.rgb[2]}"
        )

    def set_rgb(self, rgb):
        r, g, b = [int(x) for x in rgb]

        h, s, v = colorsys.rgb_to_hsv(
            r / 255,
            g / 255,
            b / 255
        )

        self.hue = round(h * 360)
        self.saturation = round(s * 100)
        self.brightness = round(v * 100)

        self.updating = True

        self.hue_slider.set(self.hue)
        self.saturation_slider.set(
            self.saturation
        )
        self.brightness_slider.set(
            self.brightness
        )

        self.updating = False
        self.update_color()

    def apply_hex(self):
        value = self.hex_entry.get().strip()

        if not re.fullmatch(
            r"#?[0-9A-Fa-f]{6}", value
        ):
            self.show_message(
                "Invalid HEX. Example: #AABBCC",
                error=True
            )
            return

        value = value.lstrip("#")

        rgb = tuple(
            int(value[i:i + 2], 16)
            for i in (0, 2, 4)
        )

        self.set_rgb(rgb)
        self.show_message("HEX color applied.")

    def save_color(self):
        name = self.name_entry.get().strip()

        if not name:
            self.show_message(
                "Enter a color name.",
                error=True
            )
            return

        success = add_custom_color(
            name,
            self.rgb
        )

        if success:
            self.name_entry.delete(0, "end")
            self.show_message(
                f"Saved: {name}"
            )
            self.refresh_saved_colors()
        else:
            self.show_message(
                "Could not save color.",
                error=True
            )

    def refresh_saved_colors(self):
        for widget in self.saved_container.winfo_children():
            widget.destroy()

        colors = load_colors()

        if not colors:
            ctk.CTkLabel(
                self.saved_container,
                text="No saved colors yet.",
                text_color="#94A3B8"
            ).pack(pady=10)
            return

        for index, color in enumerate(colors):
            rgb = color.get("rgb", [0, 0, 0])
            name = color.get("name", "Unnamed")

            if (
                not isinstance(rgb, list)
                or len(rgb) != 3
            ):
                continue

            try:
                rgb = tuple(int(x) for x in rgb)
                if any(x < 0 or x > 255 for x in rgb):
                    continue
            except (ValueError, TypeError):
                continue

            hex_value = "#{:02X}{:02X}{:02X}".format(
                *rgb
            )

            item = ctk.CTkFrame(
                self.saved_container,
                fg_color="#252B3A",
                corner_radius=10
            )
            item.pack(
                fill="x", pady=4
            )

            swatch = ctk.CTkFrame(
                item,
                width=35,
                height=35,
                fg_color=hex_value,
                corner_radius=7
            )
            swatch.pack(
                side="left",
                padx=(8, 5),
                pady=8
            )
            swatch.pack_propagate(False)

            text_frame = ctk.CTkFrame(
                item, fg_color="transparent"
            )
            text_frame.pack(
                side="left",
                fill="both",
                expand=True,
                padx=5
            )

            ctk.CTkLabel(
                text_frame,
                text=name,
                anchor="w",
                font=("Segoe UI", 12, "bold")
            ).pack(fill="x")

            ctk.CTkLabel(
                text_frame,
                text=hex_value,
                anchor="w",
                text_color="#94A3B8",
                font=("Consolas", 11)
            ).pack(fill="x")

            ctk.CTkButton(
                item,
                text="Use",
                width=45,
                height=30,
                command=lambda value=rgb:
                    self.set_rgb(value)
            ).pack(side="left", padx=3)

            ctk.CTkButton(
                item,
                text="×",
                width=30,
                height=30,
                fg_color="#991B1B",
                hover_color="#7F1D1D",
                command=lambda i=index:
                    self.delete_color(i)
            ).pack(
                side="right",
                padx=(3, 8)
            )

    def delete_color(self, index):
        colors = load_colors()

        if 0 <= index < len(colors):
            removed = colors.pop(index)
            save_colors(colors)
            self.refresh_saved_colors()

            self.show_message(
                f"Deleted: {removed.get('name', 'Color')}"
            )

    def show_message(self, message, error=False):
        self.message_label.configure(
            text=message,
            text_color=(
                "#F87171" if error else "#4ADE80"
            )
        )

