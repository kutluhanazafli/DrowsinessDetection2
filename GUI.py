from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from scipy.spatial import distance
from imutils import face_utils
import time
import dlib
import cv2
import contextlib

with contextlib.redirect_stdout(None):
    import pygame


class MainApp(MDApp):
    def varibles(self):
        pygame.mixer.init()
        pygame.mixer.music.load("audio/alert.wav")

        # Variables
        self.EYE_ASPECT_RATIO_THRESHOLD = 0.3
        self.EYE_ASPECT_RATIO_CONSEC_FRAMES = 30
        self.COUNTER = 0

        self.eye_closed_point = 0
        self.eye_open_point = 0

        # Load face cascade
        self.face_cascade = cv2.CascadeClassifier("haarcascades/haarcascade_frontalface_default.xml")

    def eye_aspect_ratio(self, eye):
        A = distance.euclidean(eye[1], eye[5])
        B = distance.euclidean(eye[2], eye[4])
        C = distance.euclidean(eye[0], eye[3])

        ear = (A+B) / (2 * C)
        return ear

    def load_face(self):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
        (self.lStart, self.lEnd) = face_utils.FACIAL_LANDMARKS_IDXS['left_eye']
        (self.rStart, self.rEnd) = face_utils.FACIAL_LANDMARKS_IDXS['right_eye']

    def build(self):
        Window.size = (400, 700)
        self.title = 'Drowsiness Detection'
        self.icon = 'icon.jpg'

        self.varibles()
        self.load_face()
        layout = MDBoxLayout(orientation='vertical')
        self.IMAGE = Image(size=(500, 400))

        layout.add_widget(self.IMAGE)

        self.RESULT_LABEL = MDLabel(
            id='my_label',
            text=f'{self.take_statistic()}',
            halign='center'
        )

        layout.add_widget(self.RESULT_LABEL)

        self.CAPTURE = cv2.VideoCapture(0)
        Clock.schedule_interval(self.load_video_with_control, 1.0/30.0)
        return layout

    def load_video_with_control(self, *args):
        ret, frame = self.CAPTURE.read()
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray, 0)
        face_rectangle = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in face_rectangle:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        for face in faces:
            shape = self.predictor(gray, face)
            shape = face_utils.shape_to_np(shape)

            left_eye = shape[self.lStart:self.lEnd]
            right_eye = shape[self.rStart:self.rEnd]

            left_eyeAspectRatio = self.eye_aspect_ratio(left_eye)
            right_eyeAspectRatio = self.eye_aspect_ratio(right_eye)
            eyeAspecRatio = (left_eyeAspectRatio + right_eyeAspectRatio) / 2

            leftEyeHull = cv2.convexHull(left_eye)
            rightEyeHull = cv2.convexHull(right_eye)

            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

            if eyeAspecRatio < self.EYE_ASPECT_RATIO_THRESHOLD:
                self.COUNTER += 1
                if self.COUNTER >= self.EYE_ASPECT_RATIO_CONSEC_FRAMES:
                    pygame.mixer.music.play(-1)
                    cv2.putText(frame, "Wake up!!", (150, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 5)
                self.eye_closed_point += 10
            else:
                self.eye_open_point += 100
                pygame.mixer.music.stop()
                self.COUNTER = 0

        buffer = cv2.flip(frame, 0).tostring()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')

        self.RESULT_LABEL.text = self.take_statistic()
        self.IMAGE.texture = texture

    def take_statistic(self):
        self.result_on_total = self.eye_closed_point + self.eye_open_point + 1
        self.open_score = self.eye_open_point * 100 / self.result_on_total
        self.closed_score = self.eye_closed_point * 100 / self.result_on_total
        text = f"WAKE RATE: {round(self.open_score)}%\nINSOMNIA RATE: {round(self.closed_score)}%"
        if self.open_score < self.closed_score:
            text += "\nIt has been determined that you are tired in the measurement made, you should take a break."
        return text


