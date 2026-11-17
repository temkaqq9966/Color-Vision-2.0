
import cv2
import time
import tkinter as tk
import customtkinter as ctk

from PIL import Image, ImageTk
from core.color_detector import detect_center_color, detect_point_color
from core.color_matcher import add_custom_color
from core.history_store import add_history


class CameraPage(ctk.CTkFrame):

    def __init__(self, master, go_back):
        super().__init__(master, fg_color="#090B12")

        self.go_back = go_back

        self.camera = None
        self.running = False
        self.frozen = False
        self.closing = False
        self.after_id = None

        self.last_frame = None
        self.current_color = None
        self.frozen_color = None

        self.selection_mode = "center"
        self.selected_point = None

        self.camera_photo = None
        self.image_x = 0
        self.image_y = 0
        self.image_width = 0
        self.image_height = 0

        # PERFORMANCE
        self.detect_interval = 0.15
        self.last_detect_time = 0
        self.frame_count = 0
        self.last_fps_time = time.perf_counter()
        self.fps = 0

        # COLOR STABILIZATION
        self.candidate_name = None
        self.candidate_count = 0
        self.stable_name = None
        self.stable_result = None
        self.required_matches = 3

        # HISTORY
        self.last_logged_name = None
        self.last_logged_time = 0
        self.history_interval = 3

        self.build_ui()

    # =====================================
    # USER INTERFACE
    # =====================================
    def build_ui(self):

        header = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        header.pack(
            fill="x", padx=25, pady=(18, 10)
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
            text="LIVE COLOR DETECTION",
            font=("Segoe UI", 24, "bold")
        ).pack(side="left", padx=20)

        self.status_label = ctk.CTkLabel(
            header,
            text="● OFFLINE",
            text_color="#F87171",
            font=("Segoe UI", 13, "bold")
        )
        self.status_label.pack(side="right")

        content = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        content.pack(
            fill="both",
            expand=True,
            padx=22,
            pady=(5, 18)
        )

        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)

        # =================================
        # LEFT PANEL
        # =================================
        left = ctk.CTkFrame(
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

        camera_header = ctk.CTkFrame(
            left, fg_color="transparent"
        )
        camera_header.pack(
            fill="x", padx=18, pady=(16, 8)
        )

        ctk.CTkLabel(
            camera_header,
            text="CAMERA PREVIEW",
            font=("Segoe UI", 15, "bold")
        ).pack(side="left")

        self.fps_label = ctk.CTkLabel(
            camera_header,
            text="0 FPS",
            text_color="#94A3B8",
            font=("Consolas", 12)
        )
        self.fps_label.pack(side="right")

        canvas_frame = ctk.CTkFrame(
            left,
            fg_color="#0F172A",
            corner_radius=12
        )
        canvas_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        self.camera_canvas = tk.Canvas(
            canvas_frame,
            bg="#0F172A",
            highlightthickness=0,
            bd=0,
            cursor="crosshair"
        )
        self.camera_canvas.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        self.camera_canvas.bind(
            "<Button-1>",
            self.on_camera_click
        )
        self.camera_canvas.bind(
            "<Configure>",
            self.on_canvas_resize
        )

        self.show_canvas_message(
            "Camera is not running"
        )

        # DETECTION MODE
        mode_frame = ctk.CTkFrame(
            left, fg_color="transparent"
        )
        mode_frame.pack(pady=(4, 8))

        self.mode_button = ctk.CTkButton(
            mode_frame,
            text="Mode: Center Detection",
            width=210,
            height=35,
            fg_color="#334155",
            command=self.toggle_selection_mode
        )
        self.mode_button.pack(
            side="left", padx=5
        )

        ctk.CTkLabel(
            mode_frame,
            text="Click on camera to select a color",
            text_color="#94A3B8",
            font=("Segoe UI", 12)
        ).pack(side="left", padx=10)

        # CAMERA CONTROLS
        controls = ctk.CTkFrame(
            left, fg_color="transparent"
        )
        controls.pack(pady=(8, 18))

        self.start_button = ctk.CTkButton(
            controls,
            text="▶ Start",
            width=100,
            height=40,
            command=self.start_camera
        )
        self.start_button.pack(
            side="left", padx=4
        )

        ctk.CTkButton(
            controls,
            text="■ Stop",
            width=90,
            height=40,
            fg_color="#374151",
            command=self.stop_camera
        ).pack(side="left", padx=4)

        self.freeze_button = ctk.CTkButton(
            controls,
            text="Freeze Color",
            width=125,
            height=40,
            fg_color="#7C3AED",
            state="disabled",
            command=self.toggle_freeze
        )
        self.freeze_button.pack(
            side="left", padx=4
        )

        # =================================
        # RIGHT PANEL
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
            text="COLOR INFORMATION",
            font=("Segoe UI", 16, "bold")
        ).pack(
            anchor="w",
            padx=18,
            pady=(20, 10)
        )

        self.color_preview = ctk.CTkFrame(
            right,
            height=95,
            fg_color="#334155",
            corner_radius=12
        )
        self.color_preview.pack(
            fill="x", padx=18, pady=8
        )
        self.color_preview.pack_propagate(False)

        self.name_label = ctk.CTkLabel(
            right,
            text="No color detected",
            font=("Segoe UI", 22, "bold")
        )
        self.name_label.pack(pady=(12, 4))

        self.source_label = ctk.CTkLabel(
            right,
            text="Waiting for camera...",
            text_color="#94A3B8"
        )
        self.source_label.pack()

        self.hex_label = ctk.CTkLabel(
            right,
            text="HEX: ---",
            font=("Consolas", 14)
        )
        self.hex_label.pack(pady=(16, 4))

        self.rgb_label = ctk.CTkLabel(
            right,
            text="RGB: ---",
            font=("Consolas", 14)
        )
        self.rgb_label.pack(pady=4)

        self.hsv_label = ctk.CTkLabel(
            right,
            text="HSV: ---",
            font=("Consolas", 14)
        )
        self.hsv_label.pack(pady=4)

        self.detection_label = ctk.CTkLabel(
            right,
            text="Detection: OFFLINE",
            text_color="#94A3B8",
            font=("Segoe UI", 12, "bold")
        )
        self.detection_label.pack(
            pady=(12, 8)
        )

        ctk.CTkLabel(
            right,
            text="SAVE CUSTOM COLOR",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(16, 8))

        self.name_entry = ctk.CTkEntry(
            right,
            placeholder_text="Enter color name",
            height=38
        )
        self.name_entry.pack(
            fill="x", padx=18
        )

        self.save_button = ctk.CTkButton(
            right,
            text="Save Frozen Color",
            height=40,
            fg_color="#16A34A",
            state="disabled",
            command=self.save_custom_color
        )
        self.save_button.pack(
            fill="x",
            padx=18,
            pady=12
        )

        self.message_label = ctk.CTkLabel(
            right,
            text="Freeze a color before saving.",
            text_color="#94A3B8",
            wraplength=250
        )
        self.message_label.pack(pady=5)

    # =====================================
    # COLOR DETECTION
    # =====================================
    def detect_color(self, frame):

        if (
            self.selection_mode == "point"
            and self.selected_point is not None
        ):
            x, y = self.selected_point
            return detect_point_color(frame, x, y)

        return detect_center_color(frame)

    def reset_stabilization(self):

        self.candidate_name = None
        self.candidate_count = 0
        self.stable_name = None
        self.stable_result = None

    def process_detection(self, result):

        name = result["name"]

        if name == self.candidate_name:
            self.candidate_count += 1
        else:
            self.candidate_name = name
            self.candidate_count = 1

        if self.candidate_count >= self.required_matches:

            self.stable_name = name
            self.stable_result = result
            self.current_color = result

            self.update_color_info(result)
            self.log_detection(result)

        elif self.stable_result is None:

            self.current_color = result
            self.update_color_info(result)

    # =====================================
    # HISTORY
    # =====================================
    def log_detection(self, result):

        now = time.perf_counter()
        name = result["name"]

        if (
            name != self.last_logged_name
            and now - self.last_logged_time
            >= self.history_interval
        ):
            try:
                add_history(
                    name,
                    result["rgb"],
                    source="Camera"
                )

                self.last_logged_name = name
                self.last_logged_time = now

            except OSError as error:
                print("History error:", error)

    # =====================================
    # START CAMERA
    # =====================================
    def start_camera(self):

        if self.running or self.closing:
            return

        self.camera = cv2.VideoCapture(
            0, cv2.CAP_DSHOW
        )

        if not self.camera.isOpened():

            self.camera.release()
            self.camera = None

            self.status_label.configure(
                text="● CAMERA ERROR",
                text_color="#F87171"
            )
            return

        self.camera.set(
            cv2.CAP_PROP_FRAME_WIDTH, 640
        )
        self.camera.set(
            cv2.CAP_PROP_FRAME_HEIGHT, 480
        )

        self.running = True
        self.frozen = False
        self.selected_point = None
        self.selection_mode = "center"
        self.current_color = None
        self.frozen_color = None

        self.reset_stabilization()

        self.last_detect_time = 0
        self.last_logged_name = None
        self.last_logged_time = 0

        self.frame_count = 0
        self.last_fps_time = time.perf_counter()

        self.mode_button.configure(
            text="Mode: Center Detection"
        )

        self.start_button.configure(
            state="disabled"
        )

        self.freeze_button.configure(
            state="normal",
            text="Freeze Color"
        )

        self.save_button.configure(
            state="disabled"
        )

        self.status_label.configure(
            text="● LIVE",
            text_color="#4ADE80"
        )

        self.detection_label.configure(
            text="Detection: LIVE",
            text_color="#4ADE80"
        )

        self.update_camera()

    # =====================================
    # UPDATE CAMERA
    # =====================================
    def update_camera(self):

        self.after_id = None

        if (
            not self.running
            or self.closing
            or self.camera is None
        ):
            return

        ret, frame = self.camera.read()

        if not ret:
            self.stop_camera()
            return

        frame = cv2.flip(frame, 1)
        self.last_frame = frame.copy()

        self.frame_count += 1
        now = time.perf_counter()

        elapsed = now - self.last_fps_time

        if elapsed >= 1:

            self.fps = self.frame_count / elapsed

            self.fps_label.configure(
                text=f"{self.fps:.1f} FPS"
            )

            self.frame_count = 0
            self.last_fps_time = now

        if (
            not self.frozen
            and now - self.last_detect_time
            >= self.detect_interval
        ):

            result = self.detect_color(frame)
            self.process_detection(result)
            self.last_detect_time = now

        self.render_frame(frame)

        if self.running and not self.closing:

            self.after_id = self.after(
                30,
                self.update_camera
            )

    # =====================================
    # MOUSE SELECTION
    # =====================================
    def on_camera_click(self, event):

        if (
            not self.running
            or self.last_frame is None
            or self.image_width <= 0
            or self.image_height <= 0
        ):
            return

        relative_x = event.x - self.image_x
        relative_y = event.y - self.image_y

        if not (
            0 <= relative_x < self.image_width
            and 0 <= relative_y < self.image_height
        ):
            return

        height, width = self.last_frame.shape[:2]

        x = int(
            relative_x * width / self.image_width
        )
        y = int(
            relative_y * height / self.image_height
        )

        x = max(0, min(x, width - 1))
        y = max(0, min(y, height - 1))

        self.selected_point = (x, y)
        self.selection_mode = "point"

        self.mode_button.configure(
            text="Mode: Selected Point"
        )

        self.reset_stabilization()

        if not self.frozen:

            result = self.detect_color(
                self.last_frame
            )
            self.process_detection(result)

        self.render_frame(self.last_frame)

    # =====================================
    # TOGGLE SELECTION MODE
    # =====================================
    def toggle_selection_mode(self):

        if self.selection_mode == "center":

            self.selection_mode = "point"

            if (
                self.selected_point is None
                and self.last_frame is not None
            ):

                h, w = self.last_frame.shape[:2]

                self.selected_point = (
                    w // 2,
                    h // 2
                )

            self.mode_button.configure(
                text="Mode: Selected Point"
            )

        else:

            self.selection_mode = "center"
            self.selected_point = None

            self.mode_button.configure(
                text="Mode: Center Detection"
            )

        self.reset_stabilization()

        if self.last_frame is not None:
            self.render_frame(self.last_frame)

    # =====================================
    # CANVAS MESSAGE
    # =====================================
    def show_canvas_message(self, message):

        self.camera_canvas.delete("all")

        width = max(
            self.camera_canvas.winfo_width(), 100
        )
        height = max(
            self.camera_canvas.winfo_height(), 100
        )

        self.camera_canvas.create_text(
            width // 2,
            height // 2,
            text=message,
            fill="#94A3B8",
            font=("Segoe UI", 15)
        )

    def on_canvas_resize(self, event):

        if self.running and self.last_frame is not None:

            self.render_frame(self.last_frame)

        elif not self.running:

            self.show_canvas_message(
                "Camera is not running"
            )

    # =====================================
    # RENDER CAMERA FRAME
    # =====================================
    def render_frame(self, frame):

        if self.closing:
            return

        frame_height, frame_width = frame.shape[:2]

        canvas_width = self.camera_canvas.winfo_width()
        canvas_height = self.camera_canvas.winfo_height()

        if canvas_width < 10 or canvas_height < 10:
            return

        scale = min(
            canvas_width / frame_width,
            canvas_height / frame_height
        )

        new_width = max(
            1, int(frame_width * scale)
        )
        new_height = max(
            1, int(frame_height * scale)
        )

        self.image_width = new_width
        self.image_height = new_height

        self.image_x = (
            canvas_width - new_width
        ) // 2

        self.image_y = (
            canvas_height - new_height
        ) // 2

        display_frame = frame.copy()

        if (
            self.selection_mode == "point"
            and self.selected_point is not None
        ):

            x, y = self.selected_point

            cv2.circle(
                display_frame,
                (x, y),
                13,
                (255, 255, 255),
                2
            )

            cv2.circle(
                display_frame,
                (x, y),
                3,
                (0, 255, 255),
                -1
            )

        else:

            cx = frame_width // 2
            cy = frame_height // 2

            cv2.rectangle(
                display_frame,
                (cx - 25, cy - 25),
                (cx + 25, cy + 25),
                (255, 255, 255),
                2
            )

        if self.frozen:

            cv2.putText(
                display_frame,
                "COLOR FROZEN",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2
            )

        rgb_frame = cv2.cvtColor(
            display_frame,
            cv2.COLOR_BGR2RGB
        )

        image = Image.fromarray(
            rgb_frame
        ).resize(
            (new_width, new_height),
            Image.Resampling.BILINEAR
        )

        self.camera_photo = ImageTk.PhotoImage(
            image
        )

        self.camera_canvas.delete("all")

        self.camera_canvas.create_image(
            self.image_x,
            self.image_y,
            anchor="nw",
            image=self.camera_photo
        )

    # =====================================
    # UPDATE COLOR INFORMATION
    # =====================================
    def update_color_info(self, result):

        rgb = result["rgb"]
        hsv = result["hsv"]

        self.color_preview.configure(
            fg_color=result["hex"]
        )

        self.name_label.configure(
            text=result["name"]
        )

        self.source_label.configure(
            text=result["source"]
        )

        self.hex_label.configure(
            text=f"HEX: {result['hex']}"
        )

        self.rgb_label.configure(
            text=(
                f"RGB: {rgb[0]}, "
                f"{rgb[1]}, {rgb[2]}"
            )
        )

        self.hsv_label.configure(
            text=(
                f"HSV: {hsv[0]}, "
                f"{hsv[1]}, {hsv[2]}"
            )
        )

    # =====================================
    # FREEZE COLOR
    # =====================================
    def toggle_freeze(self):

        if (
            not self.running
            or self.current_color is None
        ):
            return

        if not self.frozen:

            self.frozen = True

            self.frozen_color = (
                self.current_color.copy()
            )

            self.freeze_button.configure(
                text="Resume Detection",
                fg_color="#2563EB"
            )

            self.save_button.configure(
                state="normal"
            )

            self.status_label.configure(
                text="● FROZEN",
                text_color="#FBBF24"
            )

            self.detection_label.configure(
                text="Detection: FROZEN",
                text_color="#FBBF24"
            )

            self.message_label.configure(
                text="Enter a name and save the color.",
                text_color="#FBBF24"
            )

        else:
            self.resume_detection()

    # =====================================
    # RESUME DETECTION
    # =====================================
    def resume_detection(self):

        self.frozen = False
        self.frozen_color = None

        self.freeze_button.configure(
            text="Freeze Color",
            fg_color="#7C3AED"
        )

        self.save_button.configure(
            state="disabled"
        )

        self.status_label.configure(
            text="● LIVE",
            text_color="#4ADE80"
        )

        self.detection_label.configure(
            text="Detection: LIVE",
            text_color="#4ADE80"
        )

    # =====================================
    # SAVE CUSTOM COLOR
    # =====================================
    def save_custom_color(self):

        if not self.frozen or self.frozen_color is None:
            return

        name = self.name_entry.get().strip()

        if not name:

            self.message_label.configure(
                text="Enter a color name.",
                text_color="#F87171"
            )
            return

        success = add_custom_color(
            name,
            self.frozen_color["rgb"]
        )

        if success:

            self.name_entry.delete(0, "end")

            self.message_label.configure(
                text=f"Saved: {name}",
                text_color="#4ADE80"
            )

            self.resume_detection()

    # =====================================
    # STOP CAMERA
    # =====================================
    def stop_camera(self):

        self.running = False
        self.frozen = False
        self.frozen_color = None
        self.current_color = None
        self.last_frame = None

        if self.after_id is not None:

            timer = self.after_id
            self.after_id = None

            try:
                self.after_cancel(timer)
            except (ValueError, RuntimeError):
                pass

        if self.camera is not None:

            camera = self.camera
            self.camera = None
            camera.release()

        if self.closing:
            return

        self.start_button.configure(
            state="normal"
        )

        self.freeze_button.configure(
            text="Freeze Color",
            state="disabled",
            fg_color="#7C3AED"
        )

        self.save_button.configure(
            state="disabled"
        )

        self.status_label.configure(
            text="● OFFLINE",
            text_color="#F87171"
        )

        self.detection_label.configure(
            text="Detection: OFFLINE",
            text_color="#94A3B8"
        )

        self.fps_label.configure(
            text="0 FPS"
        )

        self.camera_photo = None

        self.show_canvas_message(
            "Camera is not running"
        )

    # =====================================
    # BACK TO DASHBOARD
    # =====================================
    def back(self):

        if self.closing:
            return

        self.closing = True
        self.stop_camera()
        self.go_back()

    # =====================================
    # CLEANUP
    # =====================================
    def destroy(self):

        self.closing = True
        self.stop_camera()
        super().destroy()
