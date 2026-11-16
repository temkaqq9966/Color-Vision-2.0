
import customtkinter as ctk

from core.game_engine import (
    generate_color,
    rgb_to_hex,
    calculate_score
)

from core.game_history import (
    save_game,
    load_games,
    get_best_score,
    get_game_count
)

from gui.color_picker_widget import ColorPickerWidget


BG = "#0B0F19"
PANEL = "#171D2C"
BORDER = "#293349"
TEXT = "#F8FAFC"
MUTED = "#94A3B8"
PURPLE = "#A78BFA"
GREEN = "#4ADE80"


class GamePage(ctk.CTkFrame):

    def __init__(self, master, go_back):
        super().__init__(master, fg_color=BG)

        self.go_back = go_back

        self.max_rounds = 5
        self.round_number = 0
        self.total_score = 0
        self.round_scores = []

        self.target_color = (0, 0, 0)
        self.selected_color = (128, 128, 128)

        self.phase = "idle"
        self.time_left = 0
        self.timer_id = None

        self.build_ui()
        self.update_statistics()

    def build_ui(self):

        # HEADER
        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        header.pack(
            fill="x",
            padx=28,
            pady=(18, 10)
        )

        ctk.CTkButton(
            header,
            text="← Dashboard",
            width=125,
            fg_color="#252B3A",
            hover_color="#374151",
            command=self.back
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text="COLOR MEMORY",
            font=("Segoe UI", 24, "bold"),
            text_color=TEXT
        ).pack(side="left", padx=20)

        self.round_label = ctk.CTkLabel(
            header,
            text="Round 0 / 5",
            font=("Segoe UI", 14, "bold"),
            text_color=PURPLE
        )
        self.round_label.pack(side="right")

        # STATISTICS
        stats = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        stats.pack(
            fill="x",
            padx=28,
            pady=(0, 12)
        )

        stats.grid_columnconfigure(
            (0, 1, 2),
            weight=1,
            uniform="stats"
        )

        self.best_label = self.create_stat(
            stats, 0, "BEST SCORE", "0 / 500"
        )

        self.games_label = self.create_stat(
            stats, 1, "GAMES PLAYED", "0"
        )

        self.total_label = self.create_stat(
            stats, 2, "CURRENT SCORE", "0 / 500"
        )

        # BOTTOM BAR - fixed position
        bottom = ctk.CTkFrame(
            self,
            fg_color="#111827",
            height=74
        )
        bottom.pack(
            side="bottom",
            fill="x"
        )
        bottom.pack_propagate(False)

        self.action_button = ctk.CTkButton(
            bottom,
            text="START GAME",
            width=230,
            height=44,
            corner_radius=12,
            fg_color="#8B5CF6",
            hover_color="#7C3AED",
            font=("Segoe UI", 14, "bold"),
            command=self.start_game
        )
        self.action_button.pack(pady=15)

        # SCROLLABLE CONTENT
        self.content = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.content.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 8)
        )

        game_panel = ctk.CTkFrame(
            self.content,
            fg_color=PANEL,
            corner_radius=18,
            border_width=1,
            border_color=BORDER
        )
        game_panel.pack(
            fill="x",
            pady=(0, 12)
        )

        self.status_label = ctk.CTkLabel(
            game_panel,
            text="Ready to test your color memory?",
            font=("Segoe UI", 20, "bold"),
            text_color=TEXT
        )
        self.status_label.pack(
            pady=(18, 5)
        )

        self.timer_label = ctk.CTkLabel(
            game_panel,
            text="Press START GAME",
            font=("Segoe UI", 17, "bold"),
            text_color=PURPLE
        )
        self.timer_label.pack(pady=(0, 10))

        self.color_box = ctk.CTkFrame(
            game_panel,
            width=380,
            height=110,
            fg_color="#253047",
            corner_radius=15
        )
        self.color_box.pack(
            pady=(0, 18),
            padx=15
        )
        self.color_box.pack_propagate(False)

        # COLOR PICKER
        self.picker_container = ctk.CTkFrame(
            self.content,
            fg_color=PANEL,
            corner_radius=16
        )

        self.picker = ColorPickerWidget(
            self.picker_container,
            command=self.update_color
        )
        self.picker.pack(padx=12, pady=12)

        # RESULT PANEL
        self.result_frame = ctk.CTkFrame(
            self.content,
            fg_color=PANEL,
            corner_radius=16
        )

        self.score_label = ctk.CTkLabel(
            self.result_frame,
            text="",
            font=("Segoe UI", 25, "bold"),
            text_color=GREEN
        )
        self.score_label.pack(pady=(16, 10))

        comparison = ctk.CTkFrame(
            self.result_frame,
            fg_color="transparent"
        )
        comparison.pack(pady=(0, 12))

        self.target_box = ctk.CTkFrame(
            comparison,
            width=145,
            height=75,
            corner_radius=12,
            fg_color="#253047"
        )
        self.target_box.grid(
            row=0,
            column=0,
            padx=8
        )
        self.target_box.grid_propagate(False)

        self.selected_box = ctk.CTkFrame(
            comparison,
            width=145,
            height=75,
            corner_radius=12,
            fg_color="#253047"
        )
        self.selected_box.grid(
            row=0,
            column=1,
            padx=8
        )
        self.selected_box.grid_propagate(False)

        self.target_label = ctk.CTkLabel(
            comparison,
            text="Target"
        )
        self.target_label.grid(
            row=1,
            column=0,
            pady=6
        )

        self.selected_label = ctk.CTkLabel(
            comparison,
            text="Your Color"
        )
        self.selected_label.grid(
            row=1,
            column=1,
            pady=6
        )

        # ROUND SCORE DETAILS
        self.round_details = ctk.CTkLabel(
            self.result_frame,
            text="",
            font=("Consolas", 13),
            text_color=MUTED,
            justify="center"
        )
        self.round_details.pack(
            pady=(0, 14)
        )

        # RECENT GAMES
        self.recent_frame = ctk.CTkFrame(
            self.content,
            fg_color=PANEL,
            corner_radius=16
        )
        self.recent_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        ctk.CTkLabel(
            self.recent_frame,
            text="RECENT GAMES",
            font=("Segoe UI", 15, "bold"),
            text_color=TEXT
        ).pack(
            anchor="w",
            padx=18,
            pady=(14, 6)
        )

        self.recent_list = ctk.CTkFrame(
            self.recent_frame,
            fg_color="transparent"
        )
        self.recent_list.pack(
            fill="x",
            padx=18,
            pady=(0, 12)
        )

        self.refresh_recent_games()

    def create_stat(self, parent, column, title, value):
        card = ctk.CTkFrame(
            parent,
            fg_color=PANEL,
            corner_radius=14,
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
        ).pack(pady=(12, 3))

        label = ctk.CTkLabel(
            card,
            text=value,
            font=("Segoe UI", 20, "bold"),
            text_color=TEXT
        )
        label.pack(pady=(0, 12))

        return label

    def update_statistics(self):
        self.best_label.configure(
            text=f"{get_best_score()} / 500"
        )

        self.games_label.configure(
            text=str(get_game_count())
        )

        self.total_label.configure(
            text=f"{self.total_score} / 500"
        )

    def refresh_recent_games(self):
        for widget in self.recent_list.winfo_children():
            widget.destroy()

        games = load_games()[:5]

        if not games:
            ctk.CTkLabel(
                self.recent_list,
                text="No completed games yet.",
                text_color=MUTED
            ).pack(anchor="w")
            return

        for game in games:
            row = ctk.CTkFrame(
                self.recent_list,
                fg_color="#222A3B",
                corner_radius=8
            )
            row.pack(
                fill="x",
                pady=3
            )

            ctk.CTkLabel(
                row,
                text=game.get("date", "Unknown"),
                text_color=MUTED,
                font=("Segoe UI", 12)
            ).pack(
                side="left",
                padx=12,
                pady=8
            )

            ctk.CTkLabel(
                row,
                text=f"{game.get('total_score', 0)} / 500",
                text_color=GREEN,
                font=("Segoe UI", 13, "bold")
            ).pack(
                side="right",
                padx=12
            )

    def show_picker(self):
        self.result_frame.pack_forget()
        self.recent_frame.pack_forget()

        if not self.picker_container.winfo_manager():
            self.picker_container.pack(
                fill="x",
                pady=(0, 12)
            )

    def hide_picker(self):
        self.picker_container.pack_forget()

    def show_result_panel(self):
        self.hide_picker()

        if not self.result_frame.winfo_manager():
            self.result_frame.pack(
                fill="x",
                pady=(0, 12)
            )

    def start_game(self):
        self.cancel_timer()

        self.round_number = 0
        self.total_score = 0
        self.round_scores = []

        self.update_statistics()
        self.recent_frame.pack_forget()

        self.next_round()

    def next_round(self):
        self.cancel_timer()

        self.round_number += 1

        if self.round_number > self.max_rounds:
            self.finish_game()
            return

        self.phase = "memorize"
        self.target_color = generate_color()

        self.round_label.configure(
            text=f"Round {self.round_number} / {self.max_rounds}"
        )

        self.status_label.configure(
            text="Memorize this color!"
        )

        self.hide_picker()
        self.result_frame.pack_forget()

        self.color_box.configure(
            fg_color=rgb_to_hex(self.target_color)
        )

        self.action_button.configure(
            text="MEMORIZE...",
            state="disabled",
            command=self.next_round
        )

        self.time_left = 5
        self.tick()

    def tick(self):
        self.timer_id = None

        if self.phase not in ("memorize", "guess"):
            return

        if self.time_left <= 0:
            if self.phase == "memorize":
                self.start_guessing()
            else:
                self.show_result()
            return

        self.timer_label.configure(
            text=f"{self.time_left}s"
        )

        self.time_left -= 1

        self.timer_id = self.after(
            1000,
            self.tick
        )

    def start_guessing(self):
        self.phase = "guess"
        self.time_left = 15

        self.status_label.configure(
            text="Recreate the color from memory!"
        )

        self.picker.reset_color()
        self.selected_color = self.picker.get_color()

        self.color_box.configure(
            fg_color=rgb_to_hex(self.selected_color)
        )

        self.show_picker()

        self.action_button.configure(
            text="SUBMIT COLOR",
            state="normal",
            command=self.show_result
        )

        self.tick()

    def update_color(self, rgb):
        if self.phase != "guess":
            return

        self.selected_color = tuple(rgb)

        self.color_box.configure(
            fg_color=rgb_to_hex(rgb)
        )

    def show_result(self):
        if self.phase != "guess":
            return

        self.cancel_timer()
        self.phase = "result"

        score = calculate_score(
            self.target_color,
            self.selected_color
        )

        self.round_scores.append(score)
        self.total_score += score

        self.update_statistics()

        self.status_label.configure(
            text="Round Complete!"
        )

        self.timer_label.configure(
            text=f"Round {self.round_number} finished"
        )

        self.color_box.configure(
            fg_color="#253047"
        )

        self.score_label.configure(
            text=f"+{score} / 100 POINTS"
        )

        self.target_box.configure(
            fg_color=rgb_to_hex(self.target_color)
        )

        self.selected_box.configure(
            fg_color=rgb_to_hex(self.selected_color)
        )

        self.target_label.configure(
            text=f"Target\n{rgb_to_hex(self.target_color)}"
        )

        self.selected_label.configure(
            text=f"Your Color\n{rgb_to_hex(self.selected_color)}"
        )

        self.round_details.configure(
            text=f"Total score: {self.total_score} / 500"
        )

        self.show_result_panel()

        self.action_button.configure(
            text="NEXT ROUND",
            state="normal",
            command=self.next_round
        )

    def finish_game(self):
        self.cancel_timer()
        self.phase = "finished"

        self.hide_picker()

        try:
            save_game(
                self.total_score,
                self.round_scores
            )
            saved = True
        except OSError as error:
            print("Game save error:", error)
            saved = False

        self.status_label.configure(
            text="Game Finished!"
        )

        self.timer_label.configure(
            text=(
                "Your results have been saved!"
                if saved else
                "Could not save game history."
            )
        )

        self.color_box.configure(
            fg_color="#253047"
        )

        best = get_best_score()

        self.score_label.configure(
            text=f"TOTAL: {self.total_score} / 500"
        )

        self.target_box.configure(
            fg_color="#253047"
        )

        self.selected_box.configure(
            fg_color="#253047"
        )

        self.target_label.configure(text="")
        self.selected_label.configure(text="")

        details = "\n".join(
            f"Round {i}: {score} / 100"
            for i, score in enumerate(
                self.round_scores,
                start=1
            )
        )

        details += (
            f"\n\nAVERAGE: "
            f"{self.total_score / self.max_rounds:.1f} / 100"
            f"\nBEST SCORE: {best} / 500"
        )

        self.round_details.configure(
            text=details
        )

        self.show_result_panel()

        self.update_statistics()
        self.refresh_recent_games()

        self.recent_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        self.action_button.configure(
            text="PLAY AGAIN",
            state="normal",
            command=self.start_game
        )

    def cancel_timer(self):
        if self.timer_id is not None:
            timer = self.timer_id
            self.timer_id = None

            try:
                self.after_cancel(timer)
            except (ValueError, RuntimeError):
                pass

    def back(self):
        self.cancel_timer()
        self.go_back()

    def destroy(self):
        self.cancel_timer()
        super().destroy()
