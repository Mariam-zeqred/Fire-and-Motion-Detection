import cv2
import time
import datetime
import tkinter as tk
from tkinter import filedialog
from plyer import notification

class VideoRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Recorder App")

        self.cap = cv2.VideoCapture(0)

        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.body_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_fullbody.xml")

        self.detection = False
        self.detection_stopped_time = None
        self.timer_started = False
        self.AFTER_DETECTION = 5

        self.frame_size = (int(self.cap.get(3)), int(self.cap.get(4)))
        self.fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        self.create_widgets()

    def create_widgets(self):
        self.start_button = tk.Button(
            self.root, text="Start Recording", command=self.start_recording)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(
            self.root, text="Stop Recording", command=self.stop_recording)
        self.stop_button.pack(pady=10)

        self.quit_button = tk.Button(
            self.root, text="Quit", command=self.quit_app)
        self.quit_button.pack(pady=10)

    def start_recording(self):
        self.detection = True
        current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
        self.out = cv2.VideoWriter(
            f"{current_time}.mp4", self.fourcc, 20, self.frame_size)
        print("Started Recording!")

    def stop_recording(self):
        if self.detection:
            self.detection = False
            self.timer_started = False
            self.out.release()
            print('Stop Recording!')

    def quit_app(self):
        self.stop_recording()
        self.cap.release()
        cv2.destroyAllWindows()
        self.root.destroy()

    def show_notification(self, title, message):
        notification.notify(
            title=title,
            message=message,
            app_name="Video Recorder App"
        )

    def update_frame(self):
        _, frame = self.cap.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        bodies = self.body_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) + len(bodies) > 0:
            if self.detection:
                self.timer_started = False
            else:
                self.start_recording()
                self.show_notification("Motion Detected", "Someone is in front of the camera!")
        elif self.detection:
            if self.timer_started:
                if time.time() - self.detection_stopped_time >= self.AFTER_DETECTION:
                    self.stop_recording()
            else:
                self.timer_started = True
                self.detection_stopped_time = time.time()

        if self.detection:
            self.out.write(frame)

        for (x, y, width, height) in faces:
            cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 0, 0), 3)

        for (x, y, width, height) in bodies:
            cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 3)

        cv2.imshow("Camera", frame)
        self.root.after(10, self.update_frame)


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoRecorderApp(root)
    root.protocol("WM_DELETE_WINDOW", app.quit_app)
    root.after(10, app.update_frame)
    root.mainloop()
