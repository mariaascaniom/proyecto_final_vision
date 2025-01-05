# proyecto_final_vision
Proyecto final de la asignatura de Computer Visión desarrollado por Lucía Gámir y María Ascanio

README - Proyecto de Visión por Computador

Descripción del Proyecto

Este repositorio contiene los códigos y recursos necesarios para la implementación de un sistema avanzado de visión por computador diseñado para proteger objetos de alto valor. El proyecto incluye:

Códigos Python: para la calibración de la cámara, la detección de patrones geométricos y la gestión de un sistema de seguridad con validación de secuencias.

Imágenes de calibración: conjunto de imágenes utilizadas para ajustar los parámetros intrínsecos y extrínsecos de la cámara.

El sistema detecta movimientos y reconoce una secuencia específica de formas (círculo-triángulo-cuadrado-círculo) para conceder o denegar el acceso, además de activar una alarma en caso de sabotaje o acceso no autorizado.

Contenido del Repositorio

Estructura de Archivos

📁 vision-project
│   ├── foto1.jpg
│   ├── foto2.jpg
│   └── ...
├── calibracion.py
├── seguridad.py
├── principal_final.py
└── README.md

Descripción de Archivos

calibracion.py: Contiene el script para la calibración de la cámara mediante un patrón de tablero de ajedrez. Permite obtener los parámetros intrínsecos y extrínsecos, además de corregir las distorsiones de la imagen.

seguridad.py: Implementa el sistema de validación de secuencias de patrones geométricos (círculo-triángulo-cuadrado-círculo). Si la secuencia es incorrecta, la alarma sigue activa y el sistema reinicia la validación.

principal_final.py: Script principal que integra todas las funciones del sistema. Incluye:

Detección de movimiento y sabotaje.

Activación y desactivación de la alarma mediante la "zona de desactivación".

Registro de eventos en un archivo event_log.txt.

Instrucciones de Uso

1. Requisitos Previos

Asegúrate de tener instaladas las siguientes dependencias:

pip install numpy opencv-python imageio picamera2

Además, este proyecto está diseñado para ejecutarse en un entorno con cámara, como una Raspberry Pi.

2. Calibración de la Cámara

Coloca el patrón de tablero de ajedrez frente a la cámara.

Ejecuta el archivo calibracion.py:

python calibracion.py

Se generarán imágenes con las esquinas detectadas y se mostrarán los parámetros de calibración.

3. Sistema de Seguridad

Para activar el sistema de seguridad:

Ejecuta el archivo principal_final.py:

python principal_final.py

La cámara comenzará a capturar imágenes en tiempo real.

Muestra la secuencia correcta de figuras geométricas para desactivar la alarma.

Si la cámara detecta un intento de sabotaje (como cubrirla), se activará la alarma visual.
