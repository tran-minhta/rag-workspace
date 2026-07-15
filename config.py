import os

# --- Cấu hình Mô hình ---
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_API_KEY = "ollama"
EMBEDDING_MODEL = "nomic-embed-text"
EMBEDDING_DIM = 768
LLM_MODEL = "qwen2-vl:7b"

# --- Cấu hình Voice ---
WAKE_WORD = "assistant"
SPEECH_RATE = 175  # Tốc độ đọc (TTS)

# --- Cấu hình Đường dẫn ---
RAW_DIR = "./raw_documents"
BACKUP_DIR = "./backup_documents"
STORAGE_DIR = "./local_rag_storage"

# Tự động tạo thư mục
for directory in [RAW_DIR, BACKUP_DIR, STORAGE_DIR]:
    os.makedirs(directory, exist_ok=True)
