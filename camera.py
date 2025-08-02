import os
import time
import cv2
import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage

# 📁 Carpeta de salida
OUTPUT_DIR = os.path.expanduser("~/Imágenes/InfluentCamera")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 🧠 Cargar clasificador de rostros
FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

class InfluentCameraApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.configure_gui()
        self.initialize_camera()
        self.create_layout()
        self.start_preview()

    def configure_gui(self):
        self.title("Influent Camera")
        self.geometry("800x680")
        self.minsize(720, 600)
        self.resizable(True, True)
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # ⚙️ Configuración inicial
        self.use_timer = True
        self.detect_faces = True
        self.timer_seconds = 3
        self.timer_active = False

    def initialize_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("❌ No se pudo acceder a la cámara.")
        self.frame = None
        self.recording = False
        self.video_writer = None

    def create_layout(self):
        # 🖼️ Vista previa
        self.preview_label = ctk.CTkLabel(self, text="")
        self.preview_label.pack(pady=10, expand=True)

        # ⏱️ Etiqueta de cronómetro
        self.timer_label = ctk.CTkLabel(self, text="", font=("Arial", 24))
        self.timer_label.pack()

        # 📸 Botones
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=10, fill="x", padx=20)

        self.btn_selfie = ctk.CTkButton(self.button_frame, text="📸 Tomar Selfie", command=self.prepare_selfie)
        self.btn_record = ctk.CTkButton(self.button_frame, text="🔴 Grabar", command=self.toggle_recording)
        self.btn_config = ctk.CTkButton(self.button_frame, text="⚙️ Configuración", command=self.open_config)
        self.btn_exit = ctk.CTkButton(self.button_frame, text="❌ Salir", command=self.close_app)

        for btn in [self.btn_selfie, self.btn_record, self.btn_config, self.btn_exit]:
            btn.configure(width=160, height=40, corner_radius=10)
            btn.pack(side="left", expand=True, padx=10)

    def start_preview(self):
        ret, frame = self.cap.read()
        if ret:
            self.frame = frame.copy()

            if self.detect_faces:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = FACE_CASCADE.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb).resize((640, 480))
            imgtk = CTkImage(light_image=img, size=(640, 480))
            self.preview_label.configure(image=imgtk)
            self.preview_label.image = imgtk

            if self.recording and self.video_writer:
                self.video_writer.write(self.frame)

        self.after(30, self.start_preview)

    def prepare_selfie(self):
        if self.use_timer:
            self.timer_active = True
            self.countdown(self.timer_seconds)
        else:
            self.take_selfie()

    def countdown(self, seconds):
        if seconds > 0:
            self.timer_label.configure(text=f"⏳ {seconds}")
            self.after(1000, lambda: self.countdown(seconds - 1))
        else:
            self.timer_label.configure(text="")
            self.timer_active = False
            self.take_selfie()

    def take_selfie(self):
        if self.frame is not None:
            filename = f"selfie_{int(time.time())}.png"
            path = os.path.join(OUTPUT_DIR, filename)
            cv2.imwrite(path, self.frame)
            print(f"📷 Selfie guardada en: {path}")

    def toggle_recording(self):
        if not self.recording:
            filename = f"video_{int(time.time())}.avi"
            path = os.path.join(OUTPUT_DIR, filename)
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.video_writer = cv2.VideoWriter(path, fourcc, 20.0, (self.frame.shape[1], self.frame.shape[0]))
            self.recording = True
            self.btn_record.configure(text="⏹️ Detener")
            print(f"🔴 Grabando video en: {path}")
        else:
            self.recording = False
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
            self.btn_record.configure(text="🔴 Grabar")
            print("⏹️ Grabación detenida.")

    def open_config(self):
        config_window = ctk.CTkToplevel(self)
        config_window.title("Configuración")
        config_window.geometry("300x200")
        config_window.resizable(False, False)

        # ⏱️ Cronómetro
        timer_switch = ctk.CTkSwitch(config_window, text="Usar cronómetro", command=lambda: self.toggle_setting("timer"))
        timer_switch.pack(pady=10)
        timer_switch.select() if self.use_timer else timer_switch.deselect()

        # 🧠 Detección de rostro
        face_switch = ctk.CTkSwitch(config_window, text="Detección de rostro", command=lambda: self.toggle_setting("face"))
        face_switch.pack(pady=10)
        face_switch.select() if self.detect_faces else face_switch.deselect()

    def toggle_setting(self, setting):
        if setting == "timer":
            self.use_timer = not self.use_timer
        elif setting == "face":
            self.detect_faces = not self.detect_faces

    def close_app(self):
        self.cap.release()
        if self.video_writer:
            self.video_writer.release()
        self.destroy()

    def on_closing(self):
        self.close_app()

if __name__ == "__main__":
    app = InfluentCameraApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

