import os
import subprocess
import time

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

def is_wayland():
    return os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland"

def update_bashrc():
    bashrc = os.path.expanduser("~/.bashrc")
    with open(bashrc, "r") as f:
        lines = f.readlines()

    if any("QT_QPA_PLATFORM=xcb" in line for line in lines):
        print(f"{YELLOW}⚠️ La variable QT_QPA_PLATFORM ya está configurada en .bashrc{RESET}")
        return

    with open(bashrc, "a") as f:
        f.write("\n# Forzar Qt a usar X11\nexport QT_QPA_PLATFORM=xcb\n")

    print(f"{GREEN}✅ Variable QT_QPA_PLATFORM=xcb añadida a .bashrc{RESET}")

def install_dependencies():
    print(f"{CYAN}📦 Instalando dependencias necesarias para Qt...{RESET}")
    try:
        subprocess.run([
            "sudo", "apt", "install", "-y",
            "libxcb-xinerama0", "libxcb-cursor0", "libxcb-icccm4",
            "libxcb-image0", "libxcb-keysyms1", "libxcb-render-util0", "qt5-default"
        ], check=True)
        print(f"{GREEN}✅ Dependencias instaladas correctamente.{RESET}")
    except subprocess.CalledProcessError:
        print(f"{RED}❌ Error al instalar dependencias. Intenta hacerlo manualmente.{RESET}")

def main():
    print(f"{CYAN}🔧 Configurador de entorno para apps PyQt5 en Zorin/Ubuntu{RESET}\n")

    if is_wayland():
        print(f"{YELLOW}🖥️ Estás usando Wayland. Qt puede fallar si no se fuerza a usar X11.{RESET}")
    else:
        print(f"{GREEN}🖥️ Estás usando X11. Compatible con Qt sin problemas.{RESET}")

    update_bashrc()
    install_dependencies()

    print(f"\n{MAGENTA}📝 Reinicia tu terminal o ejecuta:{RESET}")
    print(f"{CYAN}source ~/.bashrc{RESET}")
    print(f"\n{GREEN}Luego podrás ejecutar tu app con:{RESET}")
    print(f"{CYAN}python3 camera.v1.py{RESET}")

if __name__ == "__main__":
    main()

