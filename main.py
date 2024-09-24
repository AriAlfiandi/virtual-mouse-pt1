from cvzone.HandTrackingModule import HandDetector
import cv2
import math
from pynput.mouse import Controller
import screeninfo  # Untuk mendapatkan resolusi layar

# Inisialisasi mouse controller
mouse = Controller()

# Mendapatkan informasi resolusi layar
screen = screeninfo.get_monitors()[0]
screen_width, screen_height = screen.width, screen.height

# Inisialisasi kamera
cap = cv2.VideoCapture(0)

# Inisialisasi hand detector
detector = HandDetector(detectionCon=0.3, maxHands=1)

# Variabel untuk menyimpan status scroll aktif/nonaktif
scroll_active = True

while True:
    success, img = cap.read()
    if not success:
        break

    # Flip gambar secara horizontal
    img = cv2.flip(img, 1)

    # Deteksi tangan
    hands, img = detector.findHands(img)

    if hands:
        hand = hands[0]
        lmList = hand["lmList"]
        if lmList:
            # Koordinat jempol dan telunjuk
            x1, y1 = lmList[4][0], lmList[4][1]  # Jempol
            x2, y2 = lmList[8][0], lmList[8][1]  # Telunjuk

            # Menghitung panjang antara jempol dan telunjuk
            length = math.hypot(x2 - x1, y2 - y1)

            # Menggambar titik dan garis antara jempol dan telunjuk
            cv2.circle(img, (x1, y1), 5, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 5, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

            # Konversi posisi telunjuk ke koordinat layar
            screen_x = int(x2 * screen_width / img.shape[1])
            screen_y = int(y2 * screen_height / img.shape[0])

            # Menggerakkan mouse ke posisi telunjuk
            mouse.position = (screen_x, screen_y)

            # Mengecek apakah tangan menggenggam
            # Kita anggap tangan menggenggam jika semua ujung jari mendekati pusat tangan (lmList[0])
            is_fist = all(math.hypot(lmList[i][0] - lmList[0][0], lmList[i][1] - lmList[0][1]) < 40 for i in [4, 8, 12, 16, 20])

            if is_fist:
                # Ketika tangan menggenggam, toggle status scroll (aktif/nonaktif)
                scroll_active = not scroll_active
                print(f"Scroll active: {scroll_active}")

            # Scroll aktif jika status scroll_active True
            if scroll_active:
                if length < 50:
                    mouse.scroll(0, 1)  # Scroll ke atas
                    cv2.circle(img, (x2, y2), 10, (0, 255, 0), cv2.FILLED)
                elif length > 150:
                    mouse.scroll(0, -1)  # Scroll ke bawah
                    cv2.circle(img, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
                else:
                    cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)

    # Menampilkan frame
    cv2.imshow("Frame", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Melepaskan sumber daya
cap.release()
cv2.destroyAllWindows()
