import io
import os
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image
from pypdf import PdfReader, PdfWriter


class DraggableListbox(tk.Listbox):
    """Listbox that supports drag-and-drop reordering with synced data."""

    def __init__(self, master, data_ref=None, **kw):
        super().__init__(master, **kw)
        self.bind("<Button-1>", self.set_current)
        self.bind("<B1-Motion>", self.shift_selection)
        self.cur_index = None
        self.data_ref = data_ref

    def set_current(self, event):
        self.cur_index = self.nearest(event.y)

    def shift_selection(self, event):
        new_index = self.nearest(event.y)
        if new_index < 0:
            return
        if new_index == self.cur_index:
            return

        text_val = self.get(new_index)
        self.delete(new_index)
        self.insert(self.cur_index, text_val)

        if self.data_ref:
            self.data_ref[new_index], self.data_ref[self.cur_index] = (
                self.data_ref[self.cur_index],
                self.data_ref[new_index],
            )

        self.cur_index = new_index


class PDFAndImageMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF & 이미지 병합 도구")
        self.root.geometry("650x650")

        self.page_data = []

        btn_frame = tk.Frame(root, pady=10, bg="#f0f0f0")
        btn_frame.pack(fill=tk.X)

        tk.Button(
            btn_frame,
            text="📂 파일 추가 (PDF/IMG)",
            command=self.add_files,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
        ).pack(side=tk.LEFT, padx=10)
        tk.Button(
            btn_frame,
            text="❌ 선택 삭제",
            command=self.remove_selected,
            bg="#FF5252",
            fg="white",
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            btn_frame,
            text="🧹 초기화",
            command=self.clear_all,
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="▼ 아래로",
            command=self.move_down,
        ).pack(side=tk.RIGHT, padx=5)
        tk.Button(
            btn_frame,
            text="▲ 위로",
            command=self.move_up,
        ).pack(side=tk.RIGHT, padx=5)

        list_frame = tk.Frame(root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = DraggableListbox(
            list_frame,
            data_ref=self.page_data,
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 11),
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        self.status_label = tk.Label(
            root,
            text="총 0 페이지 대기 중",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        action_frame = tk.Frame(root, pady=10)
        action_frame.pack(fill=tk.X, side=tk.BOTTOM)

        tk.Button(
            action_frame,
            text="💾 PDF로 변환 및 병합 저장",
            command=self.save_pdf,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2,
        ).pack(fill=tk.X, padx=20, pady=5)

    def update_status(self):
        count = len(self.page_data)
        self.status_label.config(text=f"총 {count} 페이지 대기 중")

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="파일 선택",
            filetypes=[
                ("모든 지원 파일", "*.pdf *.jpg *.jpeg *.png *.bmp"),
                ("PDF 파일", "*.pdf"),
                ("이미지 파일", "*.jpg *.jpeg *.png *.bmp"),
            ],
        )
        if not files:
            return

        for file_path in files:
            ext = os.path.splitext(file_path)[1].lower()
            file_name = os.path.basename(file_path)

            try:
                if ext == ".pdf":
                    reader = PdfReader(file_path)
                    total_pages = len(reader.pages)
                    for i in range(total_pages):
                        display_text = f"[PDF] {file_name} - {i + 1}p"
                        self.page_data.append(
                            {
                                "type": "pdf",
                                "reader": reader,
                                "page_index": i,
                            }
                        )
                        self.listbox.insert(tk.END, display_text)
                elif ext in {".jpg", ".jpeg", ".png", ".bmp"}:
                    display_text = f"[IMG] {file_name}"
                    self.page_data.append(
                        {
                            "type": "image",
                            "path": file_path,
                            "page_index": None,
                        }
                    )
                    self.listbox.insert(tk.END, display_text)
            except Exception as exc:
                messagebox.showerror(
                    "오류",
                    f"'{file_name}' 로드 실패:\n{exc}",
                )

        self.update_status()

    def remove_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        for index in reversed(selection):
            self.listbox.delete(index)
            del self.page_data[index]
        self.update_status()

    def clear_all(self):
        self.listbox.delete(0, tk.END)
        self.page_data.clear()
        self.update_status()

    def move_up(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        if index == 0:
            return

        self.page_data[index], self.page_data[index - 1] = (
            self.page_data[index - 1],
            self.page_data[index],
        )
        text = self.listbox.get(index)
        self.listbox.delete(index)
        self.listbox.insert(index - 1, text)
        self.listbox.selection_set(index - 1)

    def move_down(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        if index == len(self.page_data) - 1:
            return

        self.page_data[index], self.page_data[index + 1] = (
            self.page_data[index + 1],
            self.page_data[index],
        )
        text = self.listbox.get(index)
        self.listbox.delete(index)
        self.listbox.insert(index + 1, text)
        self.listbox.selection_set(index + 1)

    def save_pdf(self):
        if not self.page_data:
            messagebox.showwarning("경고", "병합할 파일이 없습니다.")
            return

        save_path = filedialog.asksaveasfilename(
            title="저장",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
        )
        if not save_path:
            return

        writer = PdfWriter()

        try:
            for data in self.page_data:
                if data["type"] == "pdf":
                    reader = data["reader"]
                    idx = data["page_index"]
                    writer.add_page(reader.pages[idx])
                elif data["type"] == "image":
                    img_path = data["path"]
                    with Image.open(img_path) as img:
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")

                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format="PDF", resolution=100.0)

                        img_byte_arr.seek(0)
                        temp_reader = PdfReader(img_byte_arr)
                        writer.add_page(temp_reader.pages[0])

            writer.write(save_path)
            messagebox.showinfo("완료", "성공적으로 저장되었습니다!")
        except Exception as exc:
            messagebox.showerror(
                "오류",
                f"저장 중 오류 발생:\n{exc}",
            )
        finally:
            writer.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFAndImageMergerApp(root)
    root.mainloop()
