import speech_recognition as sr
import pyttsx3
import config

# Khởi tạo bộ đọc giọng nói Offline (pyttsx3)
try:
    engine = pyttsx3.init()
    engine.setProperty('rate', config.SPEECH_RATE)
except Exception as e:
    print(f"⚠️ Cảnh báo: Không khởi tạo được bộ phát âm thanh (TTS): {e}")
    engine = None

# Khởi tạo bộ nhận diện giọng nói (Speech Recognition)
recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = True

def speak(text: str):
    """Phát âm thanh câu trả lời ra loa"""
    print(f"🤖 Trợ lý: {text}")
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"❌ Lỗi phát âm thanh: {e}")

def listen_microphone() -> str:
    """Lắng nghe âm thanh từ microphone và chuyển thành văn bản (STT)"""
    with sr.Microphone() as source:
        # Tự động lọc nhiễu phòng trong 1 giây đầu
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("🎧 Đang lắng nghe...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            # Dùng mô hình nhận diện giọng nói tiếng Việt
            text = recognizer.recognize_google(audio, language="vi-VN")
            print(f"🗣️ Nghe được: {text}")
            return text.lower()
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""  # Không nhận dạng được âm thanh rõ ràng
        except Exception as e:
            print(f"⚠️ Lỗi Microphone: {e}")
            return ""
