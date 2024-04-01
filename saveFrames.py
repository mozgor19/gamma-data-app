import cv2
import os

def save_frames(video_path, output_folder, frame_interval=5):
    """
    Verilen video dosyasından belirli aralıklarla kareler alarak bunları belirtilen klasöre kaydeder.
    
    Args:
        video_path (str): Video dosyasının yolu.
        output_folder (str): Karelerin kaydedileceği klasörün yolu.
        frame_interval (int, optional): Her x frame'deki görüntüyü almak için kullanılan aralık. Varsayılan değer 30.

    Returns:
        int: Toplam kaydedilen kare sayısı.
    """
    # Eğer klasör yoksa oluştur
    os.makedirs(output_folder, exist_ok=True)

    # Videoyu aç
    cap = cv2.VideoCapture(video_path)

    # Başarılı bir şekilde açıldığından emin ol
    if not cap.isOpened():
        raise ValueError("Video dosyası açılamadı")

    frame_count = 0

    while True:
        # Video'dan bir frame al
        ret, frame = cap.read()

        # Video bittiğinde veya okuma başarısız olduğunda döngüyü sonlandır
        if not ret:
            break

        # Her frame_interval frame'i almak için
        if frame_count % frame_interval == 0:
            # Frame'i kaydet
            cv2.imwrite(os.path.join(output_folder, f"frame_{frame_count}.jpg"), frame)

        frame_count += 1

    # Temizleme
    cap.release()
    cv2.destroyAllWindows()

    return frame_count
