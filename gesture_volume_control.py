import cv2
import mediapipe as mp
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

# Get the volume control interface
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Function to detect finger gestures
def detect_gestures(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Check if index finger is up
            if hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_DIP].y:
                # Increase volume
                current_volume = volume.GetMasterVolumeLevelScalar()
                volume.SetMasterVolumeLevelScalar(min(current_volume + 0.05, 1.0), None)
                
            # Check if index finger is down (for volume down)
            elif hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y > hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_DIP].y:
                # Decrease volume
                current_volume = volume.GetMasterVolumeLevelScalar()
                volume.SetMasterVolumeLevelScalar(max(current_volume - 0.05, 0.0), None)
    return image

cap = cv2.VideoCapture(0)
while cap.isOpened():
    success, image = cap.read()
    if not success:
        break
    image = detect_gestures(image)
    cv2.imshow('Hand Gesture Recognition', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
