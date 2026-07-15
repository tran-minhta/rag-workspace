#!/usr/bin/env python3
import os
import sys
import glob
import asyncio
import argparse
import config
from modules.rag_core import get_rag_instance
from modules.document_handler import ingest_all_documents
from modules.voice_engine import speak, listen_microphone

# --- Mã màu ANSI để trang trí Terminal ---
BLUE = "\033[1;34m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
CYAN = "\033[1;36m"
RESET = "\033[0m"
BOLD = "\033[1m"

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

# --- MÀN HÌNH KHỞI ĐỘNG CHUẨN GEMINI CLI ---
def print_banner(mode):
    clear_screen()
    print(f"{CYAN}{'='*60}{RESET}")
    print(f"{CYAN}{BOLD}         🤖 RAG-ANYTHING OFFLINE CLI ASSISTANT{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")
    print(f" • {BOLD}Cơ sở dữ liệu:{RESET} {config.STORAGE_DIR}")
    print(f" • {BOLD}Mô hình suy luận:{RESET} {config.LLM_MODEL} ({YELLOW}{mode.upper()}{RESET})")
    print(f" • {BOLD}Mô hình nhúng:{RESET} {config.EMBEDDING_MODEL}")
    print(f"{CYAN}{'-'*60}{RESET}")
    print(f" {BOLD}Các lệnh nhanh (Slash Commands):{RESET}")
    print(f"  {GREEN}/ingest{RESET} : Quét và nạp tài liệu mới từ thư mục raw")
    print(f"  {GREEN}/voice{RESET}  : Kích hoạt trợ lý giọng nói chạy ngầm (Wake Word)")
    print(f"  {GREEN}/stats{RESET}  : Xem thống kê kho tài liệu hiện tại")
    print(f"  {GREEN}/clear{RESET}  : Dọn dẹp lịch sử hiển thị trên màn hình")
    print(f"  {GREEN}/exit{RESET}   : Thoát chương trình")
    print(f"{CYAN}{'='*60}{RESET}\n")

# --- GIAO DIỆN CHAT CLI CHÍNH ---
async def start_gemini_style_cli(rag, mode: str):
    print_banner(mode)
    history = []

    while True:
        try:
            # Dòng nhắc lệnh chuyên nghiệp
            user_input = input(f"{GREEN}👤 Bạn {RESET}› ").strip()
            if not user_input:
                continue

            # Xử lý các Slash Commands trực tiếp trong màn hình chat
            if user_input.startswith("/"):
                cmd = user_input.lower()
                if cmd == "/exit":
                    print(f"\n{YELLOW}👋 Tạm biệt! Hẹn gặp lại bạn.{RESET}")
                    break
                elif cmd == "/clear":
                    print_banner(mode)
                    continue
                elif cmd == "/stats":
                    backup_files = glob.glob(os.path.join(config.BACKUP_DIR, "*"))
                    raw_files = [f for f in backup_files if not f.endswith("_summary.md")]
                    print(f"\n{CYAN}📊 Thống kê kho tri thức:{RESET}")
                    print(f"  • Số tài liệu đã nạp: {len(raw_files)} file")
                    print(f"  • Số file tóm tắt (.md): {len(backup_files) - len(raw_files)} file\n")
                    continue
                elif cmd == "/ingest":
                    print(f"\n{YELLOW}⚙️ Đang kích hoạt tiến trình nạp tài liệu...{RESET}")
                    await ingest_all_documents(rag)
                    print()
                    continue
                elif cmd == "/voice":
                    print(f"\n{YELLOW}🎙️ Đang chuyển sang chế độ Voice Daemon...{RESET}")
                    await run_voice_daemon(rag)
                    continue
                else:
                    print(f"{RED}❌ Lệnh không hợp lệ. Hãy thử: /ingest, /voice, /stats, /clear, /exit{RESET}\n")
                    continue

            # Xử lý hội thoại thông thường
            print(f"{BLUE}⏳ Trợ lý đang suy luận...{RESET}", end="\r")
            
            context_query = user_input
            if history:
                # Giữ 4 lượt chat gần nhất làm ngữ cảnh hội thoại liên tục
                context_query = f"[Lịch sử cuộc trò chuyện]: {str(history[-4:])}\n\n[Câu hỏi mới]: {user_input}"

            response = await rag.aquery(context_query, mode=mode)
            
            # Xóa dòng "đang suy luận" và in câu trả lời đẹp mắt
            sys.stdout.write("\033[K") 
            print(f"{BLUE}{BOLD}🤖 Trợ lý:{RESET}")
            print(response)
            print(f"\n{CYAN}{'─'*60}{RESET}\n")
            
            history.append({"user": user_input, "assistant": response})

        except KeyboardInterrupt:
            print(f"\n{YELLOW}👋 Trình điều khiển kết thúc.{RESET}")
            break
        except Exception as e:
            print(f"\n{RED}❌ Lỗi: {e}{RESET}\n")

# --- HÀM CHẠY DAEMON GIỌNG NÓI ---
async def run_voice_daemon(rag):
    speak("Hệ thống nhận diện giọng nói đã sẵn sàng. Hãy nói assistant để gọi tôi.")
    print(f"\n{YELLOW}🎧 Lắng nghe từ khóa '{config.WAKE_WORD}'... (Nhấn Ctrl+C để quay lại chat CLI){RESET}")
    
    while True:
        try:
            voice_input = await asyncio.to_thread(listen_microphone)
            if config.WAKE_WORD in voice_input:
                speak("Tôi đây, tôi có thể giúp gì cho bạn?")
                question = await asyncio.to_thread(listen_microphone)
                if question:
                    speak("Đang tìm kiếm...")
                    response = await rag.aquery(question, mode="hybrid")
                    speak(response)
                else:
                    speak("Tôi không nghe rõ. Đang quay lại chế độ chờ.")
            await asyncio.sleep(0.5)
        except KeyboardInterrupt:
            print(f"\n{GREEN}✓ Đã quay lại giao diện chat CLI.{RESET}\n")
            break
        except Exception as e:
            print(f"{RED}⚠️ Lỗi: {e}{RESET}")
            await asyncio.sleep(2)

# --- KHỞI ĐỘNG CHÍNH ---
def main():
    parser = argparse.ArgumentParser(description="AI Document Assistant CLI")
    parser.add_argument(
        "--mode", type=str, default="hybrid", 
        choices=["local", "global", "hybrid", "naive"],
        help="Chế độ phân tích dữ liệu (Mặc định: hybrid)"
    )
    args = parser.parse_args()
    
    # Khởi tạo RAG Core
    rag = get_rag_instance()
    
    # Chạy thẳng vào màn hình chat mặc định
    asyncio.run(start_gemini_style_cli(rag, args.mode))

if __name__ == "__main__":
    main()
