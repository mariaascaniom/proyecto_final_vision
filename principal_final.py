from picamera2 import Picamera2
import cv2
import numpy as np
import time

# Función para verificar si un contorno está en la zona de desactivación
def is_in_deactivation_zone(contour, zone):
    x, y, w, h = cv2.boundingRect(contour)
    zone_x, zone_y, zone_w, zone_h = zone
    return zone_x <= x <= zone_x + zone_w and zone_y <= y <= zone_y + zone_h

# Función para registrar eventos
LOG_FILE = "event_log.txt"
def log_event(event_type, message):
    with open(LOG_FILE, "a") as file:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        file.write(f"{timestamp} - {event_type}: {message}\n")

# Función para verificar si la cámara está bloqueada
def is_camera_blocked(frame, threshold=0.9):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    black_pixels = np.sum(gray < 50)
    total_pixels = gray.size
    return (black_pixels / total_pixels) > threshold

if __name__ == "__main__":
    DEACTIVATION_ZONE = (200, 200, 100, 100)
    MOVEMENT_THRESHOLD = 1500
    ACTIVATION_DELAY = 2
    DEACTIVATION_DELAY = 5
    SABOTAGE_THRESHOLD = 0.9

    # Inicializar la cámara de Raspberry Pi
    picam = Picamera2()
    picam.preview_configuration.main.size = (640, 480)
    picam.preview_configuration.main.format = "RGB888"
    picam.preview_configuration.align()
    picam.configure("preview")
    picam.start()
    
    background_subtractor = cv2.createBackgroundSubtractorMOG2()
    alarm_active = False
    last_activation_time = 0
    movement_start_time = 0
    camera_blocked = False

    print("Cámara inicializada")

    while True:
        frame = picam.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (21, 21), 0)

        if is_camera_blocked(frame, threshold=SABOTAGE_THRESHOLD):
            if not camera_blocked:
                camera_blocked = True
                alarm_active = True
                log_event("Sabotage", "Camera sabotage detected: Camera blocked.")
                print("¡Sabotaje detectado por obstrucción total de la cámara!")
        else:
            if camera_blocked:
                camera_blocked = False
                alarm_active = False
                log_event("Sabotage", "Camera sabotage cleared: Camera unblocked.")
                print("¡Sabotaje despejado, cámara desbloqueada!")

        mask = background_subtractor.apply(blurred)
        _, thresh = cv2.threshold(mask, 25, 255, cv2.THRESH_BINARY)
        thresh = cv2.dilate(thresh, None, iterations=2)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        movement_detected = False
        for contour in contours:
            if cv2.contourArea(contour) > MOVEMENT_THRESHOLD:
                movement_detected = True
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                if alarm_active and is_in_deactivation_zone(contour, DEACTIVATION_ZONE):
                    alarm_active = False
                    last_activation_time = time.time()
                    log_event("Alarm", "Alarm deactivated.")
                    print("Alarma desactivada")

        current_time = time.time()
        if movement_detected:
            if movement_start_time == 0:
                movement_start_time = current_time
            elif current_time - movement_start_time >= ACTIVATION_DELAY and not alarm_active:
                if current_time - last_activation_time > DEACTIVATION_DELAY:
                    alarm_active = True
                    log_event("Alarm", "Alarm triggered.")
                    print("¡Alarma activada!")
        else:
            movement_start_time = 0

        zx, zy, zw, zh = DEACTIVATION_ZONE
        color = (0, 255, 0) if not alarm_active else (0, 0, 255)
        cv2.rectangle(frame, (zx, zy), (zx + zw, zy + zh), color, 2)
        cv2.putText(frame, "Zona de desactivacion", (zx, zy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        if camera_blocked:
            cv2.putText(frame, "SABOTAGE DETECTADO", (150, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        if camera_blocked or alarm_active:
            cv2.putText(frame, "ALARMA ACTIVADA", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        else:
            cv2.putText(frame, "Alarma desactivada", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

        cv2.imshow("Camara de Seguridad", frame)

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
