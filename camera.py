"""Universal Camera Pro: cámara multiplataforma con GUI Leviathan y modo CLI."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

try:
    from PyQt6.QtCore import QTimer, Qt
    from PyQt6.QtGui import QImage, QPixmap
    from PyQt6.QtWidgets import (
        QApplication, QComboBox, QHBoxLayout, QLabel, QMainWindow, QMessageBox,
        QPushButton, QSlider, QVBoxLayout, QWidget,
    )
except ImportError as exc:  # pragma: no cover - exercised by installation checks
    raise SystemExit("Faltan PyQt6 y sus dependencias; instale lib/requirements.txt") from exc

try:
    from leviathan_ui import CustomTitleBar, WipeWindow
except ImportError:  # Keep the app usable during development without the optional theme.
    CustomTitleBar = None
    WipeWindow = None

APP_NAME = "Universal Camera Pro"
PHOTO_DIR = Path.home() / "Pictures" / "UniversalCamera"
VIDEO_DIR = Path.home() / "Videos" / "UniversalCamera"
RESOLUTIONS = [(640, 480), (1280, 720), (1920, 1080)]
FILTERS = ("Normal", "Grises", "Sepia", "Invertir")


def discover_cameras(limit: int = 8) -> list[int]:
    found = []
    for index in range(limit):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            found.append(index)
        cap.release()
    return found


def apply_filter(frame: np.ndarray, name: str) -> np.ndarray:
    if name == "Grises":
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    if name == "Sepia":
        matrix = np.array([[0.272, 0.534, 0.131], [0.349, 0.686, 0.168], [0.393, 0.769, 0.189]])
        return np.clip(frame @ matrix.T, 0, 255).astype(np.uint8)
    if name == "Invertir":
        return cv2.bitwise_not(frame)
    return frame


def zoom_frame(frame: np.ndarray, percent: int) -> np.ndarray:
    if percent <= 100:
        return frame
    height, width = frame.shape[:2]
    factor = max(1.0, percent / 100.0)
    crop_w, crop_h = int(width / factor), int(height / factor)
    x0, y0 = (width - crop_w) // 2, (height - crop_h) // 2
    cropped = frame[y0:y0 + crop_h, x0:x0 + crop_w]
    return cv2.resize(cropped, (width, height), interpolation=cv2.INTER_LINEAR)


class CameraWindow(QMainWindow):
    def __init__(self, camera_index: int = 0) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1100, 760)
        if WipeWindow is not None:
            try:
                WipeWindow.create().set_mode("ghostBlur").set_background("auto").set_radius(12).apply(self)
            except Exception:
                pass

        self.cap: cv2.VideoCapture | None = None
        self.writer: cv2.VideoWriter | None = None
        self.recording = False
        self.face_detection = False
        self.last_frame: np.ndarray | None = None
        self.face_cascade = self._load_face_cascade()
        self.preview = QLabel("Conectando con la cámara…")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumSize(640, 420)
        self.preview.setStyleSheet("background:#111722; color:#c8d1df; border-radius:8px;")
        self.status = QLabel("Listo")
        self.camera_combo = QComboBox()
        self.resolution_combo = QComboBox()
        self.filter_combo = QComboBox()
        self.zoom = QSlider(Qt.Orientation.Horizontal)
        self.zoom.setRange(100, 300)
        self.zoom.setValue(100)
        self.zoom.setToolTip("Zoom digital")
        self.capture_button = QPushButton("Capturar")
        self.record_button = QPushButton("Grabar")
        self.face_button = QPushButton("Detección: OFF")
        self._build_ui()
        self._populate_cameras(camera_index)
        self._open_camera(self.camera_combo.currentData())
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._read_frame)
        self.timer.start(33)

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        if CustomTitleBar is not None:
            try:
                layout.addWidget(CustomTitleBar(self, title=APP_NAME))
            except Exception:
                pass
        controls = QHBoxLayout()
        self.camera_combo.currentIndexChanged.connect(lambda: self._open_camera(self.camera_combo.currentData()))
        self.resolution_combo.addItems([f"{w}×{h}" for w, h in RESOLUTIONS])
        self.resolution_combo.currentIndexChanged.connect(self._apply_resolution)
        self.filter_combo.addItems(FILTERS)
        self.capture_button.clicked.connect(self.capture_photo)
        self.record_button.clicked.connect(self.toggle_recording)
        self.face_button.clicked.connect(self.toggle_faces)
        controls.addWidget(QLabel("Cámara")); controls.addWidget(self.camera_combo)
        controls.addWidget(QLabel("Resolución")); controls.addWidget(self.resolution_combo)
        controls.addWidget(QLabel("Filtro")); controls.addWidget(self.filter_combo)
        controls.addWidget(QLabel("Zoom")); controls.addWidget(self.zoom)
        controls.addWidget(self.capture_button); controls.addWidget(self.record_button); controls.addWidget(self.face_button)
        layout.addWidget(self.preview, 1)
        layout.addLayout(controls)
        layout.addWidget(self.status)
        self.setCentralWidget(root)

    def _load_face_cascade(self):
        path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
        return cv2.CascadeClassifier(str(path)) if path.exists() else None

    def _populate_cameras(self, preferred: int) -> None:
        cameras = discover_cameras()
        self.camera_combo.clear()
        for index in cameras:
            self.camera_combo.addItem(f"Cámara {index}", index)
        if preferred in cameras:
            self.camera_combo.setCurrentIndex(cameras.index(preferred))
        if not cameras:
            self.camera_combo.addItem("Sin cámara", -1)
            self.status.setText("No se detectó ninguna cámara conectada.")

    def _open_camera(self, index) -> None:
        if self.cap is not None:
            self.cap.release()
        if index is None or int(index) < 0:
            self.cap = None
            return
        self.cap = cv2.VideoCapture(int(index))
        self._apply_resolution()
        if not self.cap.isOpened():
            self.status.setText("No se pudo abrir la cámara seleccionada.")

    def _apply_resolution(self) -> None:
        if self.cap is None or not self.cap.isOpened():
            return
        width, height = RESOLUTIONS[self.resolution_combo.currentIndex()]
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def _read_frame(self) -> None:
        if self.cap is None or not self.cap.isOpened():
            return
        ok, frame = self.cap.read()
        if not ok:
            self.status.setText("La cámara no entregó un fotograma.")
            return
        frame = zoom_frame(frame, self.zoom.value())
        if self.face_detection and self.face_cascade is not None:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            for x, y, w, h in self.face_cascade.detectMultiScale(gray, 1.1, 5):
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 220, 255), 2)
        frame = apply_filter(frame, self.filter_combo.currentText())
        self.last_frame = frame.copy()
        if self.recording and self.writer is not None:
            self.writer.write(frame)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(rgb.data, rgb.shape[1], rgb.shape[0], rgb.strides[0], QImage.Format.Format_RGB888)
        self.preview.setPixmap(QPixmap.fromImage(image).scaled(self.preview.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def _ensure_dirs(self) -> None:
        PHOTO_DIR.mkdir(parents=True, exist_ok=True)
        VIDEO_DIR.mkdir(parents=True, exist_ok=True)

    def capture_photo(self) -> None:
        if self.last_frame is None:
            self.status.setText("No hay fotograma disponible para capturar.")
            return
        self._ensure_dirs()
        path = PHOTO_DIR / f"photo-{datetime.now():%Y%m%d-%H%M%S}.jpg"
        cv2.imwrite(str(path), self.last_frame)
        self.status.setText(f"Foto guardada: {path}")

    def toggle_recording(self) -> None:
        if self.recording:
            self.recording = False
            if self.writer is not None:
                self.writer.release()
                self.writer = None
            self.record_button.setText("Grabar")
            self.status.setText("Grabación guardada.")
            return
        if self.last_frame is None:
            self.status.setText("No hay señal de cámara para grabar.")
            return
        self._ensure_dirs()
        height, width = self.last_frame.shape[:2]
        path = VIDEO_DIR / f"video-{datetime.now():%Y%m%d-%H%M%S}.avi"
        self.writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"XVID"), 24.0, (width, height))
        if not self.writer.isOpened():
            self.writer = None
            self.status.setText("No se pudo iniciar el archivo AVI.")
            return
        self.recording = True
        self.record_button.setText("Detener")
        self.status.setText(f"Grabando: {path}")

    def toggle_faces(self) -> None:
        self.face_detection = not self.face_detection
        self.face_button.setText(f"Detección: {'ON' if self.face_detection else 'OFF'}")

    def closeEvent(self, event) -> None:
        if self.writer is not None:
            self.writer.release()
        if self.cap is not None:
            self.cap.release()
        event.accept()


def cli_probe() -> int:
    cameras = discover_cameras()
    print("Cámaras detectadas:", ", ".join(map(str, cameras)) if cameras else "ninguna")
    return 0 if cameras else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=APP_NAME)
    parser.add_argument("--cli", action="store_true", help="Detectar cámaras y salir sin abrir la GUI")
    parser.add_argument("--camera", type=int, default=0, help="Índice de cámara inicial")
    args = parser.parse_args(argv)
    if args.cli:
        return cli_probe()
    app = QApplication(sys.argv if argv is None else [sys.argv[0], *argv])
    window = CameraWindow(args.camera)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
