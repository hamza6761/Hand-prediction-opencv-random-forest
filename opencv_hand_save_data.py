import cv2
import mediapipe as mp
import pandas as pd
import os
from tkinter import Tk, Entry, Button, Label
import threading

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils
current_landmarks = None  # en son tespit edilen landmark verisi

# Kamera iş parçacığı
def camera_loop():
    global current_landmarks
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        image = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)
        current_landmarks = None  # sıfırla
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                # Landmarkları düz listeye çevir
                current_landmarks = []
                for lm in hand_landmarks.landmark:
                    current_landmarks.extend([lm.x, lm.y, lm.z])
        cv2.imshow("El Takibi (ESC ile cikis yap)", image)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC ile çık
            break
    cap.release()
    cv2.destroyAllWindows()

# CSV'ye veri ekleme (comma separated value)
def save_to_csv():
    if current_landmarks:
        label = entry.get()
        if not label:
            print("Sınıf ismi girilmedi.")
            return
        df = pd.DataFrame([current_landmarks + [label]])
        df.to_csv("hand_data.csv", mode='a', header=not os.path.exists("hand_data.csv"), index=False)
        print(f"'{label}' etiketiyle veri kaydedildi.")
    else:
        print("El bulunamadı, veri kaydedilmedi.")

# Tkinter arayüz
root = Tk()
root.title("El Verisi Kaydedici")
root.geometry("400x150+50+100")  # genişlik x yükseklik + x + y
Label(root, text="Sınıf İsmi:").pack(pady=10)
entry = Entry(root, font=("Arial", 14))
entry.pack()
Button(root, text="Veriyi Kaydet (CSV)", command=save_to_csv, font=("Arial", 12)).pack(pady=20)

# Kamerayı ayrı iş parçacığında başlat
threading.Thread(target=camera_loop, daemon=True).start()
root.mainloop()