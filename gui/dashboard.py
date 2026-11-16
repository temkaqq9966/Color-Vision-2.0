
import customtkinter as ctk


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class Dashboard(ctk.CTkFrame):

    def __init__(self, master, navigate):
        super().__init__(
            master,
            fg_color="#0B0F19"
        )

        self.navigate = navigate
        self.build_ui()

    def build_ui(self):

        # FOOTER - доод талд тогтмол байрлана
        footer = ctk.CTkFrame(
            self,
            fg_color="#0B0F19",
            height=38
        )
        footer.pack(
            side="bottom",
            fill="x"
        )
        footer.pack_propagate(False)

        ctk.CTkLabel(
            footer,
            text="COLORVISION 2.0  •  MADE WITH PYTHON",
            font=("Segoe UI", 11),
            text_color="#64748B"
        ).pack(expand=True)

        # HEADER
        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        header.pack(
            fill="x",
            padx=32,
            pady=(18, 8)
        )

        brand = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )
        brand.pack(side="left")

        ctk.CTkLabel(
            brand,
            text="COLORVISION",
            font=("Segoe UI", 26, "bold"),
            text_color="#F8FAFC"
        ).pack(anchor="w")

        ctk.CTkLabel(
            brand,
            text="Explore the world of colors",
            font=("Segoe UI", 12),
            text_color="#94A3B8"
        ).pack(anchor="w", pady=(2, 0))

        ctk.CTkLabel(
            header,
            text="●  VERSION 2.0",
            font=("Segoe UI", 12, "bold"),
            text_color="#4ADE80",
            fg_color="#172B27",
            corner_radius=18,
            padx=16,
            pady=8
        ).pack(side="right")

        # HERO
        hero = ctk.CTkFrame(
            self,
            fg_color="#171D2C",
            corner_radius=18,
            border_width=1,
            border_color="#293349"
        )
        hero.pack(
            fill="x",
            padx=32,
            pady=(8, 14)
        )

        ctk.CTkLabel(
            hero,
            text="Your creative color workspace",
            font=("Segoe UI", 20, "bold"),
            text_color="#F8FAFC"
        ).pack(
            anchor="w",
            padx=22,
            pady=(16, 4)
        )

        ctk.CTkLabel(
            hero,
            text=(
                "Detect colors, challenge your memory, "
                "create palettes and explore your history."
            ),
            font=("Segoe UI", 12),
            text_color="#94A3B8"
        ).pack(
            anchor="w",
            padx=22,
            pady=(0, 12)
        )

        strip = ctk.CTkFrame(
            hero,
            fg_color="transparent"
        )
        strip.pack(
            fill="x",
            padx=22,
            pady=(0, 16)
        )

        palette = [
            "#6366F1",
            "#A855F7",
            "#EC4899",
            "#F59E0B",
            "#10B981",
            "#06B6D4"
        ]

        for color in palette:
            segment = ctk.CTkFrame(
                strip,
                height=8,
                fg_color=color,
                corner_radius=4
            )
            segment.pack(
                side="left",
                fill="x",
                expand=True,
                padx=3
            )

        # SECTION
        section = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        section.pack(
            fill="x",
            padx=32,
            pady=(0, 8)
        )

        ctk.CTkLabel(
            section,
            text="Explore Modes",
            font=("Segoe UI", 20, "bold"),
            text_color="#F8FAFC"
        ).pack(side="left")

        ctk.CTkLabel(
            section,
            text="4 available modes",
            font=("Segoe UI", 12),
            text_color="#94A3B8"
        ).pack(side="right")

        # CARDS
        cards = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        cards.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 4)
        )

        cards.grid_columnconfigure(
            0, weight=1, uniform="cards"
        )
        cards.grid_columnconfigure(
            1, weight=1, uniform="cards"
        )
        cards.grid_rowconfigure(0, weight=1)
        cards.grid_rowconfigure(1, weight=1)

        self.create_card(
            cards, 0, 0,
            "📷", "Camera Mode",
            "Recognize colors in real time",
            "#17263C", "#203856",
            "#60A5FA", "camera"
        )

        self.create_card(
            cards, 0, 1,
            "🎮", "Game Mode",
            "Challenge your color memory",
            "#2B213E", "#3C2C59",
            "#C4B5FD", "game"
        )

        self.create_card(
            cards, 1, 0,
            "🎨", "Color Picker",
            "Create and save custom colors",
            "#16352F", "#205044",
            "#5EEAD4", "picker"
        )

        self.create_card(
            cards, 1, 1,
            "◷", "History",
            "View your saved color records",
            "#382C1C", "#4D3A24",
            "#FCD34D", "history"
        )

    def create_card(
        self,
        parent,
        row,
        column,
        icon,
        title,
        subtitle,
        bg,
        hover_bg,
        accent,
        page
    ):

        card = ctk.CTkFrame(
            parent,
            fg_color=bg,
            corner_radius=16,
            border_width=1,
            border_color="#334155"
        )

        card.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=6,
            pady=6
        )

        content = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )
        content.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        icon_label = ctk.CTkLabel(
            content,
            text=icon,
            font=("Segoe UI Emoji", 25)
        )
        icon_label.pack(anchor="w")

        title_label = ctk.CTkLabel(
            content,
            text=title,
            font=("Segoe UI", 17, "bold"),
            text_color="#F8FAFC"
        )
        title_label.pack(
            anchor="w",
            pady=(5, 2)
        )

        subtitle_label = ctk.CTkLabel(
            content,
            text=subtitle,
            font=("Segoe UI", 12),
            text_color="#CBD5E1"
        )
        subtitle_label.pack(anchor="w")

        open_button = ctk.CTkButton(
            content,
            text="Open Mode  →",
            width=125,
            height=32,
            corner_radius=9,
            fg_color=accent,
            hover_color="#FFFFFF",
            text_color="#101827",
            font=("Segoe UI", 12, "bold"),
            command=lambda: self.navigate(page)
        )
        open_button.pack(
            anchor="w",
            pady=(10, 0)
        )

        # HOVER
        def on_enter(event):
            card.configure(
                fg_color=hover_bg,
                border_color=accent
            )

        def on_leave(event):
            card.configure(
                fg_color=bg,
                border_color="#334155"
            )

        for widget in (
            card,
            content,
            icon_label,
            title_label,
            subtitle_label
        ):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
