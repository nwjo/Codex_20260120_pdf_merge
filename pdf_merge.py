import tkinter as tk
from tkinter import filedialog, messagebox

from pypdf import PdfWriter


def select_files_and_merge() -> None:
    """Prompt for PDF files, then merge and save to a chosen path."""
    root = tk.Tk()
    root.withdraw()

    file_paths = filedialog.askopenfilenames(
        title="병합할 PDF 파일들을 선택하세요 (Ctrl 키를 누르고 다중 선택 가능)",
        filetypes=[("PDF files", "*.pdf")],
    )

    if not file_paths:
        print("파일이 선택되지 않았습니다.")
        return

    save_path = filedialog.asksaveasfilename(
        title="병합된 파일을 저장할 위치와 이름을 정해주세요",
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
    )

    if not save_path:
        return

    merger = PdfWriter()
    try:
        for path in file_paths:
            merger.append(path)

        merger.write(save_path)
        messagebox.showinfo(
            "성공",
            f"성공적으로 병합되었습니다!\n저장 경로: {save_path}",
        )
    except Exception as exc:
        messagebox.showerror("오류", f"작업 중 오류가 발생했습니다:\n{exc}")
    finally:
        merger.close()


if __name__ == "__main__":
    select_files_and_merge()
