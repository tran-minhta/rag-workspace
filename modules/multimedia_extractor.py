import os
import shutil
import glob
import asyncio
from datetime import datetime
from magika import Magika
import config
from modules.mineru_extractor import extract_pdf_to_markdown
# Nhập thêm module xử lý đa phương tiện vừa tạo
from modules.multimedia_extractor import extract_multimedia_to_text

magika = Magika()

async def process_single_file(rag, file_path: str):
    filename = os.path.basename(file_path)
    print(f"\n⚡ Định danh bằng Magika: {filename}...")
    
    try:
        result = await asyncio.to_thread(magika.identify_path, file_path)
        file_type = result.output.ct_label
        file_group = result.output.group
        
        print(f"🔍 Kết quả Magika: {file_type} (Nhóm: {file_group})")

        content_preview = ""
        target_rag_path = file_path
        is_multimedia = False
        transcription = ""

        # NHÁNH 1: TÀI LIỆU PHỨC TẠP (PDF / IMAGE) -> Chạy qua MinerU
        if file_type == "pdf" or file_group == "image":
            print(f"📦 Kích hoạt MinerU Engine xử lý cấu trúc sâu...")
            try:
                parsed_md_path = await extract_pdf_to_markdown(file_path)
                target_rag_path = parsed_md_path
                with open(parsed_md_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content_preview = f.read(2000)
            except Exception as mineru_err:
                print(f"⚠️ MinerU lỗi ({mineru_err}). Fallback sang mặc định.")

        # NHÁNH 2: ĐA PHƯƠNG TIỆN (AUDIO / VIDEO) -> Chạy qua STT Pipeline
        elif file_group in ['audio', 'video']:
            print(f"🎵 Kích hoạt Multimedia Engine. Đang bóc tách lời thoại (STT)...")
            is_video = (file_group == 'video')
            transcription = await extract_multimedia_to_text(file_path, is_video=is_video)
            content_preview = transcription[:2000] # Lấy đoạn đầu hội thoại để LLM đọc nhãn
            is_multimedia = True
            
            # Tạo một file text tạm chứa nội dung hội thoại để RAG nạp vào đồ thị tri thức
            temp_txt_path = f"./mineru_cache/{filename}_transcription.txt"
            with open(temp_txt_path, "w", encoding="utf-8") as f:
                f.write(transcription)
            target_rag_path = temp_txt_path

        # NHÁNH 3: CODE / VĂN BẢN THUẦN -> Đọc trực tiếp
        elif file_group in ['code', 'text'] or file_type in ['json', 'csv', 'yaml']:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content_preview = f.read(2000)
            except Exception:
                pass

        # 3. Lập chỉ mục vào RAG
        await rag.ainsert_document(target_rag_path)
        print(f"✓ {filename}: Đã lập chỉ mục vào đồ thị tri thức.")

        # 4. LLM Phân loại thông minh dựa trên ngữ cảnh đã bóc tách
        print(f"📝 {filename}: Đang lập báo cáo phân loại tệp tin...")
        analysis_prompt = (
            f"Dựa trên tệp tin thực tế:\n- Tên: {filename}\n- Loại: {file_type} (Nhóm: {file_group})\n\n"
            f"Nội dung/Lời thoại trích xuất được từ tệp tin:\n--- Begin ---\n{content_preview}\n--- End ---\n\n"
            f"Hãy trả về định dạng Markdown gồm:\n"
            f"1. **Phân loại tệp tin (Tags)**: Gán tag phù hợp như #{file_group.capitalize()}, #{file_type.upper()}\n"
            f"2. **Tóm tắt nội dung/Lời thoại chính**: Dưới 5 dòng ngắn gọn giải thích file media này nói về chủ đề gì."
        )
        analysis_result = await rag.aquery(analysis_prompt, mode="local")

        # 5. Xuất báo cáo tổng hợp và dọn dẹp vùng đệm
        summary_path = os.path.join(config.BACKUP_DIR, f"{filename}_summary.md")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(f"# Kết Quả Phân Loại Đa Phương Tiện: {filename}\n")
            f.write(f"**Thời gian:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            if is_multimedia:
                f.write(f"### 📝 Toàn bộ nội dung lời thoại (Transcription):\n{transcription}\n\n---\n")
            f.write(analysis_result)
            
        backup_path = os.path.join(config.BACKUP_DIR, filename)
        shutil.copy2(file_path, backup_path)
        os.remove(file_path)
        print(f"🗑️ {filename}: Đã hoàn tất quy trình.")

    except Exception as e:
        print(f"❌ Lỗi xử lý file '{filename}': {e}")

async def ingest_all_documents(rag):
    all_entries = glob.glob(os.path.join(config.RAW_DIR, "*"))
    files = [f for f in all_entries if os.path.isfile(f)]
        
    if not files:
        print(f"\n📭 Không tìm thấy file trong '{config.RAW_DIR}'.")
        return

    print(f"\n🚀 Khởi chạy hệ thống quét toàn diện (Magika + MinerU + VoiceSTT) cho {len(files)} tệp tin...")
    await asyncio.gather(*(process_single_file(rag, f) for f in files))
    
    # Dọn dẹp cache
    shutil.rmtree("./mineru_cache", ignore_errors=True)
    print(f"\n🎉 Quét hệ thống và đồng bộ kho lưu trữ thành công!")
