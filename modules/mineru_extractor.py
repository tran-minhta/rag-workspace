import os
import shutil
import asyncio
from magic_pdf.pipe.UNIPipe import UNIPipe
from magic_pdf.rw.DiskReaderWriter import DiskReaderWriter

def run_mineru_extraction(file_path: str, output_dir: str) -> str:
    """
    Hàm xử lý đồng bộ bóc tách PDF/Ảnh bằng MinerU.
    Trả về đường dẫn tới file markdown (.md) kết quả.
    """
    filename = os.path.basename(file_path)
    name_without_ext = os.path.splitext(filename)[0]
    
    # Đọc dữ liệu nhị phân từ file gốc
    with open(file_path, "rb") as f:
        file_bytes = f.read()
        
    # Cấu hình bộ đọc/ghi kết quả đầu ra của MinerU
    image_writer = DiskReaderWriter(os.path.join(output_dir, "images"))
    
    # Khởi tạo Pipeline xử lý của MinerU
    pipe = UNIPipe(file_bytes, {"_pdf_type": "pdf"}, image_writer)
    
    # Thực hiện phân tích cấu trúc (Layout) và chuyển đổi
    pipe.pipe_classify()
    pipe.pipe_parse()
    
    # Lấy nội dung định dạng Markdown (kèm bảng biểu, công thức)
    md_content = pipe.to_markdown()
    
    # Lưu file kết quả tạm thời
    md_output_path = os.path.join(output_dir, f"{name_without_ext}_parsed.md")
    with open(md_output_path, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    return md_output_path

async def extract_pdf_to_markdown(file_path: str) -> str:
    """Wrapper bất đồng bộ để chạy MinerU mà không gây block hệ thống"""
    tmp_output_dir = "./mineru_cache"
    os.makedirs(tmp_output_dir, exist_ok=True)
    
    # Chạy xử lý nặng trong ThreadPool để tránh treo Terminal chính
    return await asyncio.to_thread(run_mineru_extraction, file_path, tmp_output_dir)
