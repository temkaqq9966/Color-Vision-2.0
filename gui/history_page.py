
import customtkinter as ctk

from core.color_matcher import (
    load_colors,
    save_colors
)

from core.history_store import (
    load_history,
    delete_history,
    clear_history
)

from core.game_history import (
    load_games,
    get_best_score,
    delete_game,
    clear_games
)


BG = "#0B0F19"
PANEL = "#171D2C"
CARD = "#252B3A"
BORDER = "#293349"
TEXT = "#F8FAFC"
MUTED = "#94A3B8"


class HistoryPage(ctk.CTkFrame):

    def __init__(self, master, go_back):
        super().__init__(master, fg_color=BG)

        self.go_back = go_back
        self.active_tab = "saved"

        self.build_ui()
        self.refresh_data()

    def build_ui(self):
        # HEADER
        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        header.pack(
            fill="x",
            padx=25,
            pady=(18, 12)
        )

        ctk.CTkButton(
            header,
            text="← Dashboard",
            width=125,
            fg_color="#252B3A",
            command=self.go_back
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text="COLOR HISTORY",
            font=("Segoe UI", 24, "bold"),
            text_color=TEXT
        ).pack(side="left", padx=20)

        # STATISTICS
        stats = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        stats.pack(
            fill="x",
            padx=25,
            pady=(0, 12)
        )

        stats.grid_columnconfigure(
            (0, 1, 2),
            weight=1,
            uniform="stats"
        )

        self.saved_stat = self.create_stat(
            stats, 0, "SAVED COLORS"
        )

        self.detect_stat = self.create_stat(
            stats, 1, "DETECTIONS"
        )

        self.games_stat = self.create_stat(
            stats, 2, "GAMES PLAYED"
        )

        # TOOLBAR
        toolbar = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=14
        )
        toolbar.pack(
            fill="x",
            padx=25,
            pady=(0, 12)
        )

        self.tab_control = ctk.CTkSegmentedButton(
            toolbar,
            values=[
                "Saved Colors",
                "Detection History",
                "Game History"
            ],
            command=self.change_tab
        )
        self.tab_control.pack(
            side="left",
            padx=12,
            pady=12
        )
        self.tab_control.set("Saved Colors")

        self.search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="Search...",
            width=175,
            height=35
        )
        self.search_entry.pack(
            side="left",
            padx=6
        )
        self.search_entry.bind(
            "<KeyRelease>",
            lambda event: self.refresh_data()
        )

        ctk.CTkButton(
            toolbar,
            text="Refresh",
            width=75,
            fg_color="#334155",
            command=self.refresh_data
        ).pack(side="right", padx=10)

        self.clear_button = ctk.CTkButton(
            toolbar,
            text="Clear History",
            width=105,
            fg_color="#991B1B",
            hover_color="#7F1D1D",
            command=self.confirm_clear_history
        )
        self.clear_button.pack(
            side="right",
            padx=4
        )

        # SCROLLABLE LIST
        self.list_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=PANEL,
            corner_radius=16
        )
        self.list_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 10)
        )

        self.message_label = ctk.CTkLabel(
            self,
            text="",
            text_color="#4ADE80"
        )
        self.message_label.pack(pady=(0, 10))

    def create_stat(self, parent, column, title):
        card = ctk.CTkFrame(
            parent,
            fg_color=PANEL,
            corner_radius=13,
            border_width=1,
            border_color=BORDER
        )
        card.grid(
            row=0,
            column=column,
            sticky="ew",
            padx=5
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 11, "bold"),
            text_color=MUTED
        ).pack(pady=(10, 3))

        label = ctk.CTkLabel(
            card,
            text="0",
            font=("Segoe UI", 22, "bold"),
            text_color=TEXT
        )
        label.pack(pady=(0, 10))

        return label

    def change_tab(self, value):
        mapping = {
            "Saved Colors": "saved",
            "Detection History": "history",
            "Game History": "games"
        }

        self.active_tab = mapping[value]
        self.search_entry.delete(0, "end")
        self.message_label.configure(text="")
        self.refresh_data()

    def refresh_data(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        colors = load_colors()
        detections = load_history()
        games = load_games()

        self.saved_stat.configure(
            text=str(len(colors))
        )

        self.detect_stat.configure(
            text=str(len(detections))
        )

        self.games_stat.configure(
            text=str(len(games))
        )

        self.clear_button.configure(
            state=(
                "normal"
                if self.active_tab in ("history", "games")
                else "disabled"
            )
        )

        query = self.search_entry.get().strip().lower()

        if self.active_tab == "games":
            self.show_game_history(games, query)
            return

        records = (
            colors
            if self.active_tab == "saved"
            else detections
        )

        matches = []

        for index, record in enumerate(records):
            name = str(
                record.get("name", "")
            ).lower()

            hex_value = str(
                record.get("hex", "")
            ).lower()

            if query in name or query in hex_value:
                matches.append((index, record))

        if not matches:
            self.show_empty("No matching colors found.")
            return

        for index, record in matches:
            self.create_color_card(index, record)

    def show_empty(self, message):
        ctk.CTkLabel(
            self.list_frame,
            text=message,
            font=("Segoe UI", 15),
            text_color=MUTED
        ).pack(pady=35)

    # COLOR CARDS
    def create_color_card(self, index, record):
        name = str(record.get("name", "Unnamed"))
        rgb = record.get("rgb", [0, 0, 0])

        try:
            rgb = [int(value) for value in rgb]

            if len(rgb) != 3:
                return

            if any(v < 0 or v > 255 for v in rgb):
                return

        except (ValueError, TypeError):
            return

        hex_value = "#{:02X}{:02X}{:02X}".format(
            *rgb
        )

        card = ctk.CTkFrame(
            self.list_frame,
            fg_color=CARD,
            corner_radius=12
        )
        card.pack(
            fill="x",
            padx=8,
            pady=5
        )

        swatch = ctk.CTkFrame(
            card,
            width=58,
            height=58,
            fg_color=hex_value,
            corner_radius=10
        )
        swatch.pack(
            side="left",
            padx=12,
            pady=10
        )
        swatch.pack_propagate(False)

        details = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )
        details.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5,
            pady=8
        )

        ctk.CTkLabel(
            details,
            text=name,
            anchor="w",
            font=("Segoe UI", 15, "bold")
        ).pack(fill="x")

        ctk.CTkLabel(
            details,
            text=(
                f"{hex_value}   |   "
                f"RGB({rgb[0]}, {rgb[1]}, {rgb[2]})"
            ),
            anchor="w",
            text_color=MUTED,
            font=("Consolas", 12)
        ).pack(fill="x")

        if self.active_tab == "history":
            ctk.CTkLabel(
                details,
                text=(
                    f"{record.get('timestamp', '')}"
                    f"  •  {record.get('source', 'Camera')}"
                ),
                anchor="w",
                text_color=MUTED,
                font=("Segoe UI", 11)
            ).pack(fill="x")

        actions = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )
        actions.pack(side="right", padx=12)

        if self.active_tab == "saved":
            ctk.CTkButton(
                actions,
                text="Rename",
                width=75,
                height=32,
                fg_color="#475569",
                command=lambda i=index:
                    self.rename_color(i)
            ).pack(side="left", padx=4)

        ctk.CTkButton(
            actions,
            text="Delete",
            width=70,
            height=32,
            fg_color="#991B1B",
            command=lambda i=index:
                self.remove_record(i)
        ).pack(side="left", padx=4)

    def rename_color(self, index):
        colors = load_colors()

        if not (0 <= index < len(colors)):
            return

        dialog = ctk.CTkInputDialog(
            text="Enter a new color name:",
            title="Rename Color"
        )

        name = dialog.get_input()

        if name is None:
            return

        name = name.strip()

        if not name:
            self.show_message(
                "Name cannot be empty.",
                error=True
            )
            return

        colors[index]["name"] = name
        save_colors(colors)

        self.show_message("Color renamed.")
        self.refresh_data()

    def remove_record(self, index):
        if self.active_tab == "saved":
            colors = load_colors()

            if 0 <= index < len(colors):
                colors.pop(index)
                save_colors(colors)

        elif self.active_tab == "history":
            delete_history(index)

        elif self.active_tab == "games":
            try:
                deleted = delete_game(index)
            except OSError:
                self.show_message(
                    "Could not delete game history.",
                    error=True
                )
                return

            if not deleted:
                self.show_message(
                    "Game not found. Please refresh.",
                    error=True
                )
                self.refresh_data()
                return

        self.show_message("Record deleted.")
        self.refresh_data()

    # GAME HISTORY
    def show_game_history(self, games, query):
        if not games:
            self.show_empty(
                "No completed games yet."
            )
            return

        best_score = get_best_score()

        best_panel = ctk.CTkFrame(
            self.list_frame,
            fg_color="#25334A",
            corner_radius=12
        )
        best_panel.pack(
            fill="x",
            padx=8,
            pady=(8, 12)
        )

        ctk.CTkLabel(
            best_panel,
            text=f"🏆 BEST SCORE: {best_score} / 500",
            font=("Segoe UI", 19, "bold"),
            text_color="#FCD34D"
        ).pack(pady=16)

        found = False

        for index, game in enumerate(games):
            date = str(game.get("date", "Unknown"))
            total = int(game.get("total_score", 0))

            searchable = f"{date} {total}".lower()

            if query not in searchable:
                continue

            found = True

            card = ctk.CTkFrame(
                self.list_frame,
                fg_color=CARD,
                corner_radius=12
            )
            card.pack(
                fill="x",
                padx=8,
                pady=5
            )

            top = ctk.CTkFrame(
                card,
                fg_color="transparent"
            )
            top.pack(
                fill="x",
                padx=15,
                pady=(12, 8)
            )

            ctk.CTkLabel(
                top,
                text=f"Game #{len(games) - index}",
                font=("Segoe UI", 15, "bold"),
                text_color=TEXT
            ).pack(side="left")

            ctk.CTkButton(
                top,
                text="Delete",
                width=70,
                height=32,
                fg_color="#991B1B",
                hover_color="#7F1D1D",
                command=lambda i=index: self.remove_record(i)
            ).pack(side="right", padx=(12, 0))

            ctk.CTkLabel(
                top,
                text=f"{total} / 500",
                font=("Segoe UI", 20, "bold"),
                text_color="#4ADE80"
            ).pack(side="right")

            ctk.CTkLabel(
                card,
                text=date,
                text_color=MUTED,
                font=("Segoe UI", 12)
            ).pack(
                anchor="w",
                padx=15,
                pady=(0, 10)
            )

            scores = game.get("round_scores", [])

            rounds_frame = ctk.CTkFrame(
                card,
                fg_color="transparent"
            )
            rounds_frame.pack(
                fill="x",
                padx=12,
                pady=(0, 14)
            )

            rounds_frame.grid_columnconfigure(
                tuple(range(5)),
                weight=1,
                uniform="rounds"
            )

            for round_index in range(5):
                score = (
                    scores[round_index]
                    if round_index < len(scores)
                    else 0
                )

                round_box = ctk.CTkFrame(
                    rounds_frame,
                    fg_color="#334155",
                    corner_radius=8
                )
                round_box.grid(
                    row=0,
                    column=round_index,
                    sticky="ew",
                    padx=3
                )

                ctk.CTkLabel(
                    round_box,
                    text=f"R{round_index + 1}",
                    font=("Segoe UI", 11),
                    text_color=MUTED
                ).pack(pady=(7, 2))

                ctk.CTkLabel(
                    round_box,
                    text=str(score),
                    font=("Segoe UI", 15, "bold"),
                    text_color=TEXT
                ).pack(pady=(0, 7))

        if not found:
            self.show_empty(
                "No matching games found."
            )

    # CLEAR HISTORY
    def confirm_clear_history(self):
        if self.active_tab not in ("history", "games"):
            return

        is_games = self.active_tab == "games"
        history_name = "Game" if is_games else "Detection"
        clear_records = clear_games if is_games else clear_history

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Clear {history_name} History")
        dialog.geometry("360x190")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text=f"Delete all {history_name.lower()} history?",
            font=("Segoe UI", 17, "bold")
        ).pack(pady=(25, 8))

        ctk.CTkLabel(
            dialog,
            text=(
                "Saved colors and detections will remain."
                if is_games else
                "Saved colors and games will remain."
            ),
            text_color=MUTED
        ).pack(pady=(0, 20))

        buttons = ctk.CTkFrame(
            dialog,
            fg_color="transparent"
        )
        buttons.pack()

        ctk.CTkButton(
            buttons,
            text="Cancel",
            width=100,
            fg_color="#475569",
            command=dialog.destroy
        ).pack(side="left", padx=8)

        def clear_and_close():
            try:
                clear_records()
            except OSError:
                dialog.destroy()
                self.show_message(
                    f"Could not clear {history_name.lower()} history.",
                    error=True
                )
                return

            dialog.destroy()
            self.show_message(
                f"{history_name} history cleared."
            )
            self.refresh_data()

        ctk.CTkButton(
            buttons,
            text="Delete All",
            width=100,
            fg_color="#991B1B",
            command=clear_and_close
        ).pack(side="left", padx=8)

    def show_message(self, message, error=False):
        self.message_label.configure(
            text=message,
            text_color=(
                "#F87171" if error else "#4ADE80"
            )
        )
