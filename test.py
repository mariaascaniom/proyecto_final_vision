import cv2
from picamera2 import Picamera2

def stream_video():
    picam = Picamera2()
    picam.preview_configuration.main.size=(1280, 720)
    picam.preview_configuration.main.format="RGB888"
    picam.preview_configuration.align()
    picam.configure("preview")
    picam.start()
    i = 0
    while True:
        frame = picam.capture_array()
        cv2.imshow("picam", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.imwrite(f"foto{i}.jpg",frame)
            i+=1

        if cv2.waitKey(1) & 0xFF == ord('s'):

            break
    cv2.destroyAllWindows()

if __name__ == "__main__":
    stream_video()