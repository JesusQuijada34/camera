"""Diagnóstico opcional del entorno Qt para Universal Camera Pro.

No modifica .bashrc ni instala paquetes automáticamente. El usuario decide
si desea aplicar las recomendaciones mostradas.
"""
from __future__ import annotations

import importlib.util
import os
import shutil


def is_wayland() -> bool:
    return os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland"


def main() -> int:
    session = "Wayland" if is_wayland() else os.environ.get("XDG_SESSION_TYPE", "X11/unknown")
    print(f"Sesión gráfica detectada: {session}")
    print(f"QT_QPA_PLATFORM={os.environ.get('QT_QPA_PLATFORM', '<no definida>')}")
    for module in ("cv2", "numpy", "PyQt6", "leviathan_ui"):
        state = "disponible" if importlib.util.find_spec(module) else "ausente"
        print(f"{module}: {state}")
    if shutil.which("python") is None and shutil.which("python3") is None:
        print("No se encontró un intérprete Python en PATH.")
        return 1
    print("Si Qt falla en Wayland, pruebe QT_QPA_PLATFORM=xcb solo para esa ejecución.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
