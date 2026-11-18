
import customtkinter as ctk

from core.game_engine import (
    generate_color,
    rgb_to_hex,
    calculate_score
)

from gui.color_picker_widget import ColorPickerWidget


class GamePage(ctk.CTkFrame):

    def __init__(self, master, go_back):
        super().__init__(master, fg_color="#090B12")

        self.go_back = go_back

        self.max_rounds = 5
        self.target_color = (0, 0, 0)
        self.selected_color = (128, 128, 128)

        self.round_number = 0
        self.total_score = 0

        self.phase = "idle"
        self.time_left = 0
        self.timer_id = None

        self.build_ui()

    # =====================================
    # USER INTERFACE
    # =====================================
    def build_ui(self):

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        header.pack(
            fill="x",
            padx=25,
            pady=(12, 5)
        )

        ctk.CTkButton(
            header,
            text="← Dashboard",
            width=130,
            fg_color="#252B3A",
            command=self.back
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text="COLOR MEMORY",
            font=("Segoe UI", 24, "bold")
        ).pack(side="left", padx=25)

        self.round_label = ctk.CTkLabel(
            header,
            text=f"Round 0 / {self.max_rounds}",
            font=("Segoe UI", 15)
        )
        self.round_label.pack(side="right")

        # BOTTOM ACTION BAR
        bottom = ctk.CTkFrame(
            self,
            fg_color="#111827",
            height=75
        )
        bottom.pack(
            side="bottom",
            fill="x"
        )
        bottom.pack_propagate(False)

        self.action_button = ctk.CTkButton(
            bottom,
            text="START GAME",
            width=220,
            height=44,
            corner_radius=12,
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
            padx=20,
            pady=5
        )

        self.status_label = ctk.CTkLabel(
            self.content,
            text="Ready to test your color memory?",
            font=("Segoe UI", 20, "bold")
        )
        self.status_label.pack(pady=(12, 5))

        self.timer_label = ctk.CTkLabel(
            self.content,
            text="",
            font=("Segoe UI", 29, "bold"),
            text_color="#60A5FA"
        )
        self.timer_label.pack(pady=5)

        # COLOR PREVIEW
        self.color_box = ctk.CTkFrame(
            self.content,
            width=380,
            height=105,
            fg_color="#1E293B",
            corner_radius=15
        )
        self.color_box.pack(pady=8)
        self.color_box.pack_propagate(False)

        # GAME COLOR PICKER
        # RGB, HEX, HSV Finder харагдахгүй.
        self.picker = ColorPickerWidget(
            self.content,
            command=self.update_color,
            show_finders=False
        )

        # RESULT PANEL
        self.result_frame = ctk.CTkFrame(
            self.content,
            fg_color="#171C2A",
            corner_radius=15
        )

        self.score_label = ctk.CTkLabel(
            self.result_frame,
            text="",
            font=("Segoe UI", 27, "bold"),
            text_color="#4ADE80"
        )
        self.score_label.pack(pady=(15, 10))

        comparison = ctk.CTkFrame(
            self.result_frame,
            fg_color="transparent"
        )
        comparison.pack(padx=20, pady=10)

        self.target_box = ctk.CTkFrame(
            comparison,
            width=160,
            height=85,
            corner_radius=12
        )
        self.target_box.grid(
            row=0,
            column=0,
            padx=10
        )
        self.target_box.grid_propagate(False)

        self.selected_box = ctk.CTkFrame(
            comparison,
            width=160,
            height=85,
            corner_radius=12
        )
        self.selected_box.grid(
            row=0,
            column=1,
            padx=10
        )
        self.selected_box.grid_propagate(False)

        self.target_label = ctk.CTkLabel(
            comparison,
            text="Target",
            font=("Segoe UI", 12)
        )
        self.target_label.grid(
            row=1,
            column=0,
            pady=5
        )

        self.selected_label = ctk.CTkLabel(
            comparison,
            text="Your Color",
            font=("Segoe UI", 12)
        )
        self.selected_label.grid(
            row=1,
            column=1,
            pady=5
        )

    # =====================================
    # PICKER VISIBILITY
    # =====================================
    def show_picker(self):

        self.result_frame.pack_forget()

        if not self.picker.winfo_manager():
            self.picker.pack(pady=10)

    def hide_picker(self):

        if self.picker.winfo_manager():
            self.picker.pack_forget()

    def show_result_panel(self):

        self.hide_picker()

        if not self.result_frame.winfo_manager():
            self.result_frame.pack(pady=10)

    # =====================================
    # START GAME
    # =====================================
    def start_game(self):

        self.cancel_timer()

        self.round_number = 0
        self.total_score = 0

        self.next_round()

    # =====================================
    # NEXT ROUND
    # =====================================
    def next_round(self):

        self.cancel_timer()

        self.round_number += 1

        if self.round_number > self.max_rounds:
            self.finish_game()
            return

        self.phase = "memorize"
        self.target_color = generate_color()

        self.round_label.configure(
            text=(
                f"Round {self.round_number} / "
                f"{self.max_rounds}"
            )
        )

        self.status_label.configure(
            text="Memorize this color!"
        )
        self.timer_label.configure(text="")

        self.hide_picker()
        self.result_frame.pack_forget()

        self.action_button.configure(
            text="MEMORIZE...",
            state="disabled"
        )

        self.color_box.configure(
            fg_color=rgb_to_hex(self.target_color)
        )

        self.time_left = 5
        self.tick()

    # =====================================
    # TIMER
    # =====================================
    def tick(self):

        self.timer_id = None

        if self.time_left <= 0:

            if self.phase == "memorize":
                self.start_guessing()

            elif self.phase == "guess":
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

    # =====================================
    # GUESSING
    # =====================================
    def start_guessing(self):

        self.phase = "guess"
        self.time_left = 7

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

    # =====================================
    # UPDATE SELECTED COLOR
    # =====================================
    def update_color(self, rgb):

        if self.phase != "guess":
            return

        self.selected_color = tuple(rgb)

        self.color_box.configure(
            fg_color=rgb_to_hex(self.selected_color)
        )

    # =====================================
    # SHOW ROUND RESULT
    # =====================================
    def show_result(self):

        if self.phase != "guess":
            return

        self.cancel_timer()
        self.phase = "result"

        score = calculate_score(
            self.target_color,
            self.selected_color
        )

        self.total_score += score

        self.status_label.configure(
            text="Round Complete!"
        )
        self.timer_label.configure(text="")

        self.color_box.configure(
            fg_color="#1E293B"
        )

        self.score_label.configure(
            text=f"{score} / 100 POINTS"
        )

        self.target_box.configure(
            fg_color=rgb_to_hex(self.target_color)
        )

        self.selected_box.configure(
            fg_color=rgb_to_hex(self.selected_color)
        )

        self.target_label.configure(
            text=(
                f"Target\n"
                f"{rgb_to_hex(self.target_color)}"
            )
        )

        self.selected_label.configure(
            text=(
                f"Your Color\n"
                f"{rgb_to_hex(self.selected_color)}"
            )
        )

        self.show_result_panel()

        self.action_button.configure(
            text="NEXT ROUND",
            state="normal",
            command=self.next_round
        )

    # =====================================
    # FINISH GAME
    # =====================================
    def finish_game(self):

        self.phase = "finished"
        self.cancel_timer()

        self.hide_picker()

        self.status_label.configure(
            text="Game Finished!"
        )
        self.timer_label.configure(text="")

        self.color_box.configure(
            fg_color="#1E293B"
        )

        self.score_label.configure(
            text=(
                f"TOTAL: {self.total_score} / "
                f"{self.max_rounds * 100}\n"
                f"AVERAGE: "
                f"{self.total_score / self.max_rounds:.1f} / 100"
            )
        )

        self.target_box.configure(
            fg_color="#1E293B"
        )

        self.selected_box.configure(
            fg_color="#1E293B"
        )

        self.target_label.configure(text="")
        self.selected_label.configure(text="")

        self.show_result_panel()

        self.action_button.configure(
            text="PLAY AGAIN",
            state="normal",
            command=self.start_game
        )

    # =====================================
    # TIMER CLEANUP
    # =====================================
    def cancel_timer(self):

        if self.timer_id is not None:

            self.after_cancel(self.timer_id)
            self.timer_id = None

    # =====================================
    # BACK
    # =====================================
    def back(self):

        self.cancel_timer()
        self.go_back()

    # =====================================
    # DESTROY
    # =====================================
    def destroy(self):

        self.cancel_timer()
        super().destroy()
