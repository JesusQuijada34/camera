import cv2
import customtkinter as ctk
import numpy as np
import os
import platform
import time
from PIL import Image, ImageTk
from threading import Thread

class UniversalCameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Influent Camera Selfie - Pro Edition")

        # Configuración inicial
        self.min_width = 1024
        self.min_height = 600
        self.corner_radius = 3
        self.setup_window()

        # Configuración de apariencia
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Configuración de la cámara
        self.cap = None
        self.current_filter = "normal"
        self.recording = False
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = None
        self.zoom_factor = 1.0
        self.face_detection = True
        self.camera_index = 0
        self.camera_resolution = (640, 480)

        # Cargar clasificador de rostros
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Configuración de directorios
        self.setup_directories()

        # Configuración de la interfaz principal
        self.setup_main_ui()

        # Iniciar la cámara
        self.init_camera()

        # Configuración de la ventana de configuración
        self.settings_window = None

        # Manejar redimensionamiento
        self.root.bind("<Configure>", self.on_window_resize)

    def setup_window(self):
        """Configura la ventana principal con tamaño mínimo"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Tamaño inicial (80% del mínimo o de la pantalla si es más pequeña)
        init_width = min(int(self.min_width * 0.8), screen_width)
        init_height = min(int(self.min_height * 0.8), screen_height)

        self.root.geometry(f"{init_width}x{init_height}")
        self.root.minsize(self.min_width, self.min_height)

        # Centrar la ventana
        x = (screen_width - init_width) // 2
        y = (screen_height - init_height) // 2
        self.root.geometry(f"+{x}+{y}")

    def setup_directories(self):
        """Configura las rutas de guardado multiplataforma"""
        home = os.path.expanduser("~")
        system = platform.system()

        # Directorios base según sistema operativo
        if system == "Windows":
            self.images_dir = os.path.join(home, "Pictures", "UniversalCamera")
            self.videos_dir = os.path.join(home, "Videos", "UniversalCamera")
        elif system == "Darwin":  # macOS
            self.images_dir = os.path.join(home, "Pictures", "UniversalCamera")
            self.videos_dir = os.path.join(home, "Movies", "UniversalCamera")
        else:  # Linux y otros
            self.images_dir = os.path.join(home, "Pictures", "UniversalCamera")
            self.videos_dir = os.path.join(home, "Videos", "UniversalCamera")

        # Verificar nombres en español/inglés
        possible_image_names = ["Pictures", "Imágenes", "Images", "Fotos"]
        possible_video_names = ["Videos", "Vídeos", "Movies", "Películas"]

        # Buscar directorio de imágenes
        for name in possible_image_names:
            test_path = os.path.join(home, name)
            if os.path.exists(test_path):
                self.images_dir = os.path.join(test_path, "UniversalCamera")
                break

        # Buscar directorio de videos
        for name in possible_video_names:
            test_path = os.path.join(home, name)
            if os.path.exists(test_path):
                self.videos_dir = os.path.join(test_path, "UniversalCamera")
                break

        # Crear directorios si no existen
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.videos_dir, exist_ok=True)

    def init_camera(self):
        """Inicializa la cámara con la configuración actual"""
        if self.cap is not None:
            self.cap.release()

        self.cap = cv2.VideoCapture(self.camera_index)
        if self.camera_resolution:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_resolution[1])

        # Actualizar vista de cámara si ya está configurada la UI
        if hasattr(self, 'camera_view'):
            self.update_camera()

    def setup_main_ui(self):
        """Configura la interfaz principal"""
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=self.corner_radius)
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Configurar grid layout
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Barra superior
        self.top_bar = ctk.CTkFrame(
            self.main_frame,
            height=50,
            corner_radius=self.corner_radius,
            fg_color="#007aff"
        )
        self.top_bar.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.top_bar.grid_columnconfigure(1, weight=1)

        # Botón de menú
        self.menu_btn = ctk.CTkButton(
            self.top_bar,
            text="☰",
            width=40,
            height=40,
            corner_radius=self.corner_radius,
            fg_color="transparent",
            hover_color="#005bbf",
            command=self.open_settings
        )
        self.menu_btn.grid(row=0, column=0, padx=5, pady=5)

        # Título
        self.title_label = ctk.CTkLabel(
            self.top_bar,
            text="Influent Camera Selfie - Pro Edition",
            font=("Arial", 16, "bold"),
            text_color="white"
        )
        self.title_label.grid(row=0, column=1, pady=5)

        # Vista de la cámara
        self.camera_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=self.corner_radius,
            fg_color="black"
        )
        self.camera_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

        self.camera_view = ctk.CTkLabel(self.camera_frame, text="")
        self.camera_view.pack(fill="both", expand=True, padx=2, pady=2)

        # Panel de controles
        self.control_panel = ctk.CTkFrame(
            self.main_frame,
            height=80,
            corner_radius=self.corner_radius
        )
        self.control_panel.grid(row=2, column=0, sticky="nsew", padx=2, pady=2)

        # Configurar grid para controles
        self.control_panel.grid_columnconfigure(0, weight=1)
        self.control_panel.grid_columnconfigure(1, weight=1)
        self.control_panel.grid_columnconfigure(2, weight=1)

        # Botón de captura
        self.capture_btn = ctk.CTkButton(
            self.control_panel,
            text="CAPTURAR",
            height=50,
            corner_radius=self.corner_radius,
            fg_color="#34c759",
            hover_color="#248a3d",
            font=("Arial", 14, "bold"),
            command=self.capture_photo
        )
        self.capture_btn.grid(row=0, column=1, padx=5, pady=5)

        # Botón de grabación
        self.record_btn = ctk.CTkButton(
            self.control_panel,
            text="GRABAR",
            height=50,
            corner_radius=self.corner_radius,
            fg_color="#ff3b30",
            hover_color="#d70015",
            font=("Arial", 14, "bold"),
            command=self.toggle_recording
        )
        self.record_btn.grid(row=0, column=2, padx=5, pady=5, sticky="e")

        # Botón de detección facial
        self.face_btn = ctk.CTkButton(
            self.control_panel,
            text="DETECCIÓN: ON",
            height=30,
            corner_radius=self.corner_radius,
            fg_color="#007aff",
            hover_color="#005bbf",
            command=self.toggle_face_detection
        )
        self.face_btn.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        # Control de zoom
        self.zoom_frame = ctk.CTkFrame(
            self.control_panel,
            fg_color="transparent"
        )
        self.zoom_frame.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="e")

        ctk.CTkLabel(self.zoom_frame, text="Zoom:").pack(side="left", padx=(0, 5))

        self.zoom_slider = ctk.CTkSlider(
            self.zoom_frame,
            from_=100,
            to=300,
            number_of_steps=20,
            width=150,
            command=self.adjust_zoom
        )
        self.zoom_slider.set(100)
        self.zoom_slider.pack(side="left")

        # Barra de estado
        self.status_bar = ctk.CTkFrame(
            self.main_frame,
            height=30,
            corner_radius=self.corner_radius
        )
        self.status_bar.grid(row=3, column=0, sticky="nsew", padx=2, pady=2)

        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text=f"Fotos: {self.images_dir} | Videos: {self.videos_dir}",
            text_color="gray"
        )
        self.status_label.pack(side="left", padx=10)

    def open_settings(self):
        """Abre la ventana de configuración"""
        if self.settings_window is not None:
            self.settings_window.focus()
            return

        self.settings_window = ctk.CTkToplevel(self.root)
        self.settings_window.title("Configuración")
        self.settings_window.geometry("400x500")
        self.settings_window.resizable(False, False)
        self.settings_window.protocol("WM_DELETE_WINDOW", self.close_settings)

        # Frame principal
        settings_frame = ctk.CTkFrame(
            self.settings_window,
            corner_radius=self.corner_radius
        )
        settings_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Configuración de cámara
        ctk.CTkLabel(
            settings_frame,
            text="Configuración de Cámara",
            font=("Arial", 14, "bold")
        ).pack(pady=10)

        # Selección de cámara
        ctk.CTkLabel(settings_frame, text="Cámara:").pack(pady=(10, 0))
        self.cam_selector = ctk.CTkComboBox(
            settings_frame,
            values=self.get_available_cameras(),
            command=self.change_camera
        )
        self.cam_selector.pack(pady=5)
        self.cam_selector.set(f"Cámara {self.camera_index}")

        # Resolución
        ctk.CTkLabel(settings_frame, text="Resolución:").pack(pady=(10, 0))
        self.res_selector = ctk.CTkComboBox(
            settings_frame,
            values=["640x480", "800x600", "1024x768", "1280x720", "1920x1080"],
            command=self.change_resolution
        )
        self.res_selector.pack(pady=5)
        self.res_selector.set(f"{self.camera_resolution[0]}x{self.camera_resolution[1]}")

        # Configuración de filtros
        ctk.CTkLabel(
            settings_frame,
            text="Filtros",
            font=("Arial", 14, "bold")
        ).pack(pady=(20, 10))

        filters_frame = ctk.CTkFrame(
            settings_frame,
            fg_color="transparent"
        )
        filters_frame.pack(pady=5)

        self.filter_btns = []
        filters = [
            ("Normal", "normal"),
            ("Grises", "gray"),
            ("Sepia", "sepia"),
            ("Invertir", "invert")
        ]

        for i, (text, filter_name) in enumerate(filters):
            btn = ctk.CTkButton(
                filters_frame,
                text=text,
                width=80,
                height=30,
                corner_radius=self.corner_radius,
                fg_color="#e5e5ea" if filter_name != self.current_filter else "#007aff",
                text_color="black" if filter_name != self.current_filter else "white",
                hover_color="#d1d1d6",
                command=lambda fn=filter_name: self.apply_filter(fn)
            )
            btn.grid(row=0, column=i, padx=5)
            self.filter_btns.append(btn)

        # Configuración de directorios
        ctk.CTkLabel(
            settings_frame,
            text="Directorios",
            font=("Arial", 14, "bold")
        ).pack(pady=(20, 10))

        ctk.CTkLabel(settings_frame, text="Fotos:").pack(pady=(5, 0))
        self.images_dir_label = ctk.CTkLabel(
            settings_frame,
            text=self.images_dir,
            text_color="gray",
            wraplength=380
        )
        self.images_dir_label.pack(pady=5)

        ctk.CTkLabel(settings_frame, text="Videos:").pack(pady=(5, 0))
        self.videos_dir_label = ctk.CTkLabel(
            settings_frame,
            text=self.videos_dir,
            text_color="gray",
            wraplength=380
        )
        self.videos_dir_label.pack(pady=5)

        # Botón de cerrar
        ctk.CTkButton(
            settings_frame,
            text="Cerrar",
            corner_radius=self.corner_radius,
            command=self.close_settings
        ).pack(pady=20)

    def close_settings(self):
        """Cierra la ventana de configuración"""
        if self.settings_window:
            self.settings_window.destroy()
            self.settings_window = None

    def get_available_cameras(self):
        """Devuelve una lista de cámaras disponibles"""
        max_test = 5
        available = []
        for i in range(max_test):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(f"Cámara {i}")
                cap.release()
        return available

    def change_camera(self, choice):
        """Cambia la cámara seleccionada"""
        try:
            index = int(choice.split()[-1])
            if index != self.camera_index:
                self.camera_index = index
                self.init_camera()
        except:
            pass

    def change_resolution(self, choice):
        """Cambia la resolución de la cámara"""
        try:
            width, height = map(int, choice.split('x'))
            self.camera_resolution = (width, height)
            self.init_camera()
        except:
            pass

    def update_camera(self):
        """Actualiza la vista de la cámara"""
        if self.cap is None:
            return

        ret, frame = self.cap.read()
        if ret:
            # Aplicar zoom
            h, w = frame.shape[:2]
            new_h, new_w = int(h / self.zoom_factor), int(w / self.zoom_factor)
            x1, y1 = (w - new_w) // 2, (h - new_h) // 2
            frame = frame[y1:y1+new_h, x1:x1+new_w]
            frame = cv2.resize(frame, (w, h))

            # Detección facial
            if self.face_detection:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)

                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)

            # Aplicar filtros
            if self.current_filter == "gray":
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
            elif self.current_filter == "sepia":
                frame = self.apply_sepia(frame)
            elif self.current_filter == "invert":
                frame = cv2.bitwise_not(frame)
            else:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convertir para Tkinter
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            self.camera_view.imgtk = imgtk
            self.camera_view.configure(image=imgtk)

            # Si estamos grabando, guardar el frame
            if self.recording and self.out is not None:
                self.out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

        self.root.after(30, self.update_camera)

    def apply_sepia(self, frame):
        """Aplica filtro sepia"""
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        kernel = np.array([[0.272, 0.534, 0.131],
                          [0.349, 0.686, 0.168],
                          [0.393, 0.769, 0.189]])
        frame = cv2.transform(frame, kernel)
        frame = np.clip(frame, 0, 255)
        return frame

    def toggle_face_detection(self):
        """Activa/desactiva la detección facial"""
        self.face_detection = not self.face_detection
        if self.face_detection:
            self.face_btn.configure(text="DETECCIÓN: ON", fg_color="#007aff")
        else:
            self.face_btn.configure(text="DETECCIÓN: OFF", fg_color="#a7a7a7")

    def apply_filter(self, filter_name):
        """Aplica el filtro seleccionado"""
        self.current_filter = filter_name

        # Actualizar botones en la ventana de configuración
        if self.settings_window:
            for btn in self.filter_btns:
                if btn.cget("text").lower() == filter_name.lower():
                    btn.configure(fg_color="#007aff", text_color="white")
                else:
                    btn.configure(fg_color="#e5e5ea", text_color="black")

    def adjust_zoom(self, value):
        """Ajusta el zoom digital"""
        self.zoom_factor = value / 100

    def capture_photo(self):
        """Captura una foto"""
        if self.cap is None:
            return

        ret, frame = self.cap.read()
        if ret:
            # Aplicar detección facial si está activa
            if self.face_detection:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)

            # Aplicar el filtro actual
            if self.current_filter == "gray":
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
            elif self.current_filter == "sepia":
                frame = self.apply_sepia(frame)
            elif self.current_filter == "invert":
                frame = cv2.bitwise_not(frame)
            else:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Guardar la foto
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.images_dir, f"photo_{timestamp}.jpg")
            cv2.imwrite(filename, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

            # Mostrar notificación
            self.show_notification("Foto capturada", f"Guardada en:\n{filename}")

    def toggle_recording(self):
        """Inicia/detiene la grabación de video"""
        if self.cap is None:
            return

        self.recording = not self.recording
        if self.recording:
            self.record_btn.configure(text="DETENER", fg_color="#ff3b30")
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.videos_dir, f"video_{timestamp}.avi")
            frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.out = cv2.VideoWriter(filename, self.fourcc, 20.0, (frame_width, frame_height))

            # Actualizar estado
            self.status_label.configure(text=f"GRABANDO... {filename}", text_color="red")
        else:
            self.record_btn.configure(text="GRABAR", fg_color="#34c759")
            if self.out is not None:
                self.out.release()
                self.out = None
                filename = os.path.join(self.videos_dir, f"video_{timestamp}.avi")
                self.show_notification("Grabación guardada", f"Guardada en:\n{filename}")
                self.status_label.configure(
                    text=f"Fotos: {self.images_dir} | Videos: {self.videos_dir}",
                    text_color="gray"
                )

    def show_notification(self, title, message):
        """Muestra una notificación emergente"""
        notification = ctk.CTkToplevel(self.root)
        notification.title(title)
        notification.geometry("400x120")
        notification.resizable(False, False)

        ctk.CTkLabel(
            notification,
            text=title,
            font=("Arial", 16, "bold")
        ).pack(pady=5)

        ctk.CTkLabel(
            notification,
            text=message,
            font=("Arial", 12)
        ).pack(pady=5)

        ctk.CTkButton(
            notification,
            text="OK",
            corner_radius=self.corner_radius,
            command=notification.destroy
        ).pack(pady=10)

        notification.transient(self.root)
        notification.grab_set()
        self.root.wait_window(notification)

    def on_window_resize(self, event):
        """Maneja el redimensionamiento de la ventana"""
        if event.widget == self.root:
            # Aquí puedes agregar lógica de redimensionamiento si es necesario
            pass

    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        if self.cap is not None:
            self.cap.release()
        if self.out is not None:
            self.out.release()
        if self.settings_window:
            self.settings_window.destroy()
        self.root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = UniversalCameraApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
