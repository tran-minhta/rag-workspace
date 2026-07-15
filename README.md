# rag-workspace
datacenter from anything
# RAG-Anything Offline Workspace

Hệ thống quản lý và truy vấn tài liệu đa phương thức (Multimodal RAG) hoạt động hoàn toàn ngoại tuyến (Offline), được tối ưu hóa cho môi trường Linux cục bộ sử dụng **Ollama** và **RAG-Anything**.

Hệ thống tự động bóc tách văn bản, bảng biểu, công thức toán học (LaTeX) và hình ảnh (sử dụng Vision LLM để mô tả nội dung ảnh), sau đó tự động dọn dẹp file thô để tiết kiệm tài nguyên bộ nhớ cục bộ.

---

## 🛠️ Yêu cầu hệ thống

* **Hệ điều hành:** Linux (Ubuntu/Debian) hoặc môi trường máy ảo độc lập.
* **Trình quản lý gói:** `uv` (Astral) để cài đặt siêu tốc và cô lập môi trường.
* **Mô hình chạy Local:** Ollama (đã kéo sẵn các model cần thiết).

---

## 🚀 Hướng dẫn cài đặt & Thiết lập môi trường

### Bước 1: Khởi động Ollama và tải Models
Đảm bảo Ollama đang chạy ngầm trên máy của bạn và tải xuống các mô hình sau:

```bash
# Mô hình Vision để đọc hiểu ảnh/sơ đồ và suy luận chính
ollama pull qwen2-vl:7b

# Mô hình nhúng (Embeddings) để vector hóa văn bản (768 chiều)
ollama pull nomic-embed-text
