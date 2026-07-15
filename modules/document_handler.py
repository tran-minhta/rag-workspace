import os
import shutil
import glob
import asyncio
from datetime import datetime
import config

async def process_single_file(rag, file_path: str):
    filename = os.path.basename(file_path)
    print(f"\n⚡ Đang nạp: {filename}...")
    
    try:
        # 1. Thêm vào RAG DB
        await rag.ainsert_document(file_path)
        print(f"✓ {filename}: Đã lập chỉ mục tri thức thành công.")

        # 2. Tạo nhãn & tóm tắt tự động
        print(f"📝 {filename}: Đang phân tích nội dung để gán nhãn và tóm tắt...")
        analysis_prompt = (
            f"Dựa trên nội dung của tài liệu '{filename}' vừa nạp, hãy trả về kết quả định dạng Markdown gồm:\n"
            f"1. **Phân loại/Nhãn (Tags)**: (Ví dụ: #Code, #Sách_Kỹ_Thuật, #Sơ_Đồ...)\n"
            f"2. **Tóm tắt cốt lõi**: (Dưới 5 ý chính quan trọng nhất)"
        )
        analysis_result = await rag.aquery(analysis_prompt, mode="local")

        # Lưu bản tóm tắt gọn gàng ra file Markdown riêng biệt
        summary_path = os.path.join(config.BACKUP_DIR, f"{filename}_summary.md")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(f"# Tổng Quan Tài Liệu: {filename}\n")
            f.write(f"**Ngày cập nhật:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(analysis_result)
        print(f"💾 {filename}: Đã xuất file tóm tắt nhanh tại: {summary_path}")

        # 3. Sao lưu file thô ban đầu
        backup_path = os.path.join(config.BACKUP_DIR, filename)
        shutil.copy2(file_path, backup_path)
        
        # 4. Xóa file gốc tại thư mục raw
        os.remove(file_path)
        print(f"🗑️ {filename}: Đã dọn dẹp file thô gốc.")

    except Exception as e:
        print(f"❌ Thất bại khi xử lý file '{filename}': {e}")

async def ingest_all_documents(rag):
    extensions = ["*.pdf", "*.docx", "*.pptx", "*.xlsx", "*.png", "*.jpg", "*.jpeg"]
    files = []
    for ext in extensions:
        files.extend(glob.glob(os.path.join(config.RAW_DIR, ext)))
        
    if not files:
        print(f"\n📭 Thư mục '{config.RAW_DIR}' trống trơn!")
        return

    print(f"\n🚀 Trợ lý phát hiện {len(files)} tài liệu mới. Đang xử lý đồng thời...")
    
    # Xử lý song song
    await asyncio.gather(*(process_single_file(rag, f) for f in files))
    
    # Dọn dẹp cache rác
    for cache_dir in ["./pdf_parse_cache", "./mineru_cache"]:
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir, ignore_errors=True)
            
    print(f"\n{'-'*40}\n🎉 Trợ lý đã hoàn tất nạp dữ liệu và dọn dẹp sạch sẽ bộ nhớ tạm!")
