
import customtkinter as ctk

from gui.dashboard import Dashboard
from gui.game_page import GamePage
from gui.camera_page import CameraPage
from gui.picker_page import PickerPage
from gui.history_page import HistoryPage


class ColorVisionApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("ColorVision 2.0")
        self.geometry("1100x750")
        self.minsize(950, 650)

        self.configure(
            fg_color="#090B12"
        )

        self.current_page = None
        self.show_dashboard()

    def clear_page(self):
        if self.current_page is not None:
            page = self.current_page
            self.current_page = None
            page.destroy()

    def show_dashboard(self):
        self.clear_page()

        self.current_page = Dashboard(
            self,
            navigate=self.navigate
        )

        self.current_page.pack(
            fill="both",
            expand=True
        )

    def navigate(self, page):
        self.clear_page()

        if page == "camera":
            self.current_page = CameraPage(
                self,
                go_back=self.show_dashboard
            )

        elif page == "game":
            self.current_page = GamePage(
                self,
                go_back=self.show_dashboard
            )

        elif page == "picker":
            self.current_page = PickerPage(
                self,
                go_back=self.show_dashboard
            )

        elif page == "history":
            self.current_page = HistoryPage(
                self,
                go_back=self.show_dashboard
            )

        else:
            self.show_dashboard()
            return

        self.current_page.pack(
            fill="both",
            expand=True
        )


if __name__ == "__main__":
    app = ColorVisionApp()
    app.mainloop()
