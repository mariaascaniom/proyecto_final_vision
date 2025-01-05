import cv2
import numpy as np
from picamera2 import Picamera2

class PasswordValidator:
    def __init__(self, correct_sequence):
        self.correct_sequence = correct_sequence
        self.detected_sequence = []

    def add_pattern(self, pattern):
        if len(self.detected_sequence) == 0 or self.detected_sequence[-1] != pattern:
            self.detected_sequence.append(pattern)

    def validate(self):
        if len(self.detected_sequence) == len(self.correct_sequence):
            if self.detected_sequence == self.correct_sequence:
                return True
            else:
                return False
        return None

    def reset(self):
        self.detected_sequence = []


def preprocess_image(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
    img_thresh = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 11, 2)
    return img_thresh


def detect_shapes(img):
    shapes = []
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
        area = cv2.contourArea(contour)

        if area > 500:  # Detectar figuras pequeñas
            if len(approx) == 3:
                shapes.append(("triangle", contour))
            elif len(approx) == 4:
                shapes.append(("square", contour))
            else:
                (x, y), radius = cv2.minEnclosingCircle(contour)
                if 0.8 * radius**2 * np.pi <= area <= 1.2 * radius**2 * np.pi:
                    shapes.append(("circle", contour))

    return shapes


def stream_video(correct_sequence):
    picam = Picamera2()
    picam.preview_configuration.main.size = (1280, 720)
    picam.preview_configuration.main.format = "RGB888"
    picam.preview_configuration.align()
    picam.configure("preview")
    picam.start()

    validator = PasswordValidator(correct_sequence)

    print("Cámara inicializada. Muestra los patrones para validar la contraseña.")

    try:
        while True:
            frame = picam.capture_array()
            img_preprocessed = preprocess_image(frame)

            detected_shapes = detect_shapes(img_preprocessed)

            if detected_shapes:
                for shape, contour in detected_shapes:
                    cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.putText(frame, shape, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    validator.add_pattern(shape)
                
                print(f"Secuencia detectada: {validator.detected_sequence}")

            # Validación de la contraseña cada cuatro figuras
            if len(validator.detected_sequence) == len(correct_sequence):
                if validator.validate():
                    print("¡Acceso permitido! Contraseña correcta.")
                    cv2.putText(frame, "CONTRASEÑA CORRECTA", (150, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
                else:
                    print("Acceso denegado. Contraseña incorrecta.")
                    cv2.putText(frame, "CONTRASEÑA INCORRECTA", (150, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                
                cv2.imshow("Pattern Detection", frame)
                cv2.waitKey(2000)
                validator.reset()

            cv2.imshow("Pattern Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Saliendo...")
                break

    finally:
        picam.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    correct_sequence = ["circle", "triangle", "square", "circle"]
    stream_video(correct_sequence)
