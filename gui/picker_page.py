
import customtkinter as ctk

from core.color_matcher import (
    load_colors,
    save_colors,
    add_custom_color
)

from gui.color_picker_widget import ColorPickerWidget


class PickerPage(ctk.CTkFrame):

    def __init__(self, master, go_back):
        super().__init__(
            master,
            fg_color="#090B12"
        )

        self.go_back = go_back
        self.rgb = (66, 135, 245)
        self.hex_color = "#4287F5"

        self.build_ui()
        self.refresh_saved_colors()

    # =====================================
    # MAIN UI
    # =====================================
    def build_ui(self):

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        header.pack(
            fill="x",
            padx=25,
            pady=(20, 12)
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
        ).pack(
            side="left",
            padx=25
        )

        content = ctk.CTkFrame(
            self,
            fg_color="transparent"
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

        # =================================
        # LEFT PANEL - COLOR PICKER
        # =================================
        left = ctk.CTkScrollableFrame(
            content,
            fg_color="#171C2A",
            corner_radius=18
        )
        left.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 10)
        )

        # Шинэ RGB / HEX / HSV Finder
        self.picker = ColorPickerWidget(
            left,
            command=self.on_color_change
        )
        self.picker.pack(
            fill="x",
            padx=5,
            pady=5
        )

        # =================================
        # RIGHT PANEL - SAVE COLOR
        # =================================
        right = ctk.CTkScrollableFrame(
            content,
            fg_color="#171C2A",
            corner_radius=18
        )
        right.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        ctk.CTkLabel(
            right,
            text="SAVE COLOR",
            font=("Segoe UI", 17, "bold")
        ).pack(
            anchor="w",
            padx=18,
            pady=(20, 12)
        )

        self.name_entry = ctk.CTkEntry(
            right,
            placeholder_text="Color name",
            height=40
        )
        self.name_entry.pack(
            fill="x",
            padx=18
        )

        ctk.CTkButton(
            right,
            text="Save Color",
            height=40,
            fg_color="#16A34A",
            hover_color="#15803D",
            command=self.save_color
        ).pack(
            fill="x",
            padx=18,
            pady=10
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
            anchor="w",
            padx=18,
            pady=(15, 10)
        )

        self.saved_container = ctk.CTkFrame(
            right,
            fg_color="transparent"
        )
        self.saved_container.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

    # =====================================
    # COLOR CHANGE
    # =====================================
    def on_color_change(self, rgb):

        self.rgb = tuple(
            int(value) for value in rgb
        )

        self.hex_color = "#{:02X}{:02X}{:02X}".format(
            *self.rgb
        )

    # =====================================
    # SET RGB
    # =====================================
    def set_rgb(self, rgb):

        r, g, b = (
            int(value) for value in rgb
        )

        if any(
            value < 0 or value > 255
            for value in (r, g, b)
        ):
            raise ValueError(
                "RGB values must be between 0 and 255"
            )

        self.picker.set_rgb(r, g, b)

    # =====================================
    # SAVE COLOR
    # =====================================
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

    # =====================================
    # SAVED COLORS
    # =====================================
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

            rgb = color.get(
                "rgb",
                [0, 0, 0]
            )

            name = color.get(
                "name",
                "Unnamed"
            )

            if (
                not isinstance(rgb, (list, tuple))
                or len(rgb) != 3
            ):
                continue

            try:
                rgb = tuple(
                    int(value) for value in rgb
                )

                if any(
                    value < 0 or value > 255
                    for value in rgb
                ):
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
                fill="x",
                pady=4
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
                item,
                fg_color="transparent"
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

            # USE COLOR
            ctk.CTkButton(
                item,
                text="Use",
                width=45,
                height=30,
                command=lambda value=rgb:
                    self.set_rgb(value)
            ).pack(
                side="left",
                padx=3
            )

            # DELETE COLOR
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

    # =====================================
    # DELETE COLOR
    # =====================================
    def delete_color(self, index):

        colors = load_colors()

        if 0 <= index < len(colors):

            removed = colors.pop(index)

            save_colors(colors)

            self.refresh_saved_colors()

            self.show_message(
                f"Deleted: {removed.get('name', 'Color')}"
            )

    # =====================================
    # MESSAGE
    # =====================================
    def show_message(self, message, error=False):

        self.message_label.configure(
            text=message,
            text_color=(
                "#F87171"
                if error
                else "#4ADE80"
            )
        )
