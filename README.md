## **Descripción Completa de la Aplicación: Universal Camera Pro**  

### **📌 Visión General**  
**Camera Selfie** es una aplicación multiplataforma (Windows, macOS, Linux) que combina funciones avanzadas de cámara, reconocimiento facial, grabación de video y captura de fotos con una interfaz intuitiva estilo iOS/macOS. Está diseñada para funcionar en cualquier resolución desde **1024x600** y se integra perfectamente con las carpetas de imágenes y videos del sistema operativo, independientemente del idioma.  

---

## **🎯 Características Principales**  

### **1. 🎥 Vista de Cámara en Tiempo Real**  
- Compatible con múltiples cámaras (webcams, cámaras externas).  
- Ajuste de **resolución** (640x480, 1280x720, 1920x1080, etc.).  
- **Zoom digital** controlable mediante un slider.  
- **Detección facial** en tiempo real con marcadores amarillos.  

### **2. 📸 Captura de Fotos**  
- Guarda imágenes automáticamente en la carpeta **`Pictures/Imágenes`** del sistema.  
- Nombres de archivo con **timestamp** para evitar duplicados.  
- Filtros aplicables:  
  - **Normal** (sin filtro).  
  - **Escala de grises** (blanco y negro).  
  - **Sepia** (tono vintage).  
  - **Invertir colores** (efecto negativo).  

### **3. 🎬 Grabación de Video**  
- Formato de salida: **`.avi`** (compatible con la mayoría de reproductores).  
- Guarda grabaciones en la carpeta **`Videos/Vídeos`** del sistema.  
- Indicador visual de grabación en rojo.  

### **4. ⚙️ Menú de Configuración**  
- **Selección de cámara**: Cambia entre cámaras disponibles.  
- **Ajuste de resolución**: Optimiza calidad vs rendimiento.  
- **Filtros**: Previsualización y aplicación en tiempo real.  
- **Rutas de guardado**: Muestra las ubicaciones de fotos y videos.  

### **5. 🖥️ Interfaz Adaptable**  
- Diseño **responsive** que se ajusta desde **1024x600** hasta 4K.  
- **Esquinas redondeadas (3px)** en todos los elementos.  
- **Modo claro/oscuro** (según configuración del sistema).  

---

## **🛠️ Funcionamiento Detallado**  

### **🔹 Inicio y Configuración Inicial**  
1. **Al abrir la app**, detecta automáticamente:  
   - Cámaras disponibles.  
   - Carpetas de imágenes/videos (en inglés o español).  
   - Resolución óptima según la pantalla.  
2. **Si no hay una cámara conectada**, muestra un mensaje de error.  

### **🔹 Uso Básico**  
| **Botón**         | **Función** |
|-------------------|------------|
| **☰ Menú**        | Abre configuración avanzada. |
| **CAPTURAR**      | Toma una foto y la guarda en `Pictures/UniversalCamera`. |
| **GRABAR**        | Inicia/detiene la grabación de video (guardado en `Videos/UniversalCamera`). |
| **DETECCIÓN: ON/OFF** | Activa/desactiva el reconocimiento facial. |
| **Zoom Slider**   | Ajusta el nivel de zoom digital (100%-300%). |

### **🔹 Menú de Configuración (⚙️)**  
- **Selección de cámara**: Cambia entre dispositivos de captura.  
- **Resolución**: Ajusta entre 640x480, 1280x720, etc.  
- **Filtros**: Permite previsualizar efectos antes de aplicarlos.  
- **Rutas de archivos**: Muestra dónde se guardan fotos/videos.  

---

## **📂 Gestión de Archivos**  
- Las **fotos** se guardan en:  
  - Windows: `C:\Users\[Usuario]\Pictures\UniversalCamera\`  
  - macOS: `/Users/[Usuario]/Pictures/UniversalCamera/`  
  - Linux: `/home/[Usuario]/Imágenes/UniversalCamera/`  

- Los **videos** se guardan en:  
  - Windows: `C:\Users\[Usuario]\Videos\UniversalCamera\`  
  - macOS: `/Users/[Usuario]/Movies/UniversalCamera/`  
  - Linux: `/home/[Usuario]/Videos/UniversalCamera/`  

*(Si las carpetas no existen, la aplicación las crea automáticamente.)*  

---

## **🚀 Requisitos del Sistema**  
- **Python 3.8+**  
- **Bibliotecas necesarias**:  
  ```bash
  pip install opencv-python customtkinter pillow numpy
  ```
- **Sistemas soportados**: Windows 10/11, macOS (Intel/M1), Linux (Ubuntu, Fedora, etc.).  

---

## **🔍 Posibles Mejoras Futuras**  
✅ **Modo retrato** con desenfoque de fondo.  
✅ **Efectos AR** (máscaras, filtros divertidos).  
✅ **Subida automática a la nube** (Google Drive, Dropbox).  
✅ **Soporte para streaming** (RTMP, YouTube Live).  

---

## **🎬 Conclusión**  
**Camera Selfie** es una solución **todo en uno** para:  
✔ Captura de fotos con filtros.  
✔ Grabación de video estable.  
✔ Reconocimiento facial en tiempo real.  
✔ Compatibilidad total con cualquier sistema operativo.  

---

Here are the **requirements** to run **Universal Camera Pro**:

### 📋 **Python Dependencies**
Install these libraries via `pip`:
```bash
pip install opencv-python customtkinter pillow numpy
```
or

```bash
autorun/.bat
```

### 🖥️ **System Requirements**
- **Python 3.8 or higher**  
- **Operating Systems**:  
  - ✅ **Windows 10/11**  
  - ✅ **macOS** (Intel & Apple Silicon)  
  - ✅ **Linux** (Ubuntu, Fedora, etc.)  
- **Minimum Resolution**: **1024×600** (works on smaller screens but optimized for HD+)  
- **Webcam** (built-in or external)  

### 🔧 **Additional Notes**
- The app **auto-detects** system folders (supports both English/Spanish paths like `Pictures/Imágenes`).  
- No admin permissions needed (portable, stores files in user directories).  

### ⚠️ **Troubleshooting**
- If **OpenCV fails** to detect the camera:  
  ```bash
  pip install --upgrade opencv-python-headless
  ```
- For **Linux users**, ensure `libgtk-3-dev` is installed:  
  ```bash
  sudo apt-get install libgtk-3-dev  # Ubuntu/Debian
  ```

---

🚀 **Ready to run!** Just execute the Python script after installing dependencies.  
```bash
python camera.py
```
