import os
import tkinter as tk
from tkinter import filedialog, messagebox

from pypdf import PdfReader, PdfWriter


class DraggableListbox(tk.Listbox):
    """Listbox that supports drag-and-drop reordering."""

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.bind("<Button-1>", self.set_current)
        self.bind("<B1-Motion>", self.shift_selection)
        self.cur_index = None

    def set_current(self, event):
        self.cur_index = self.nearest(event.y)

    def shift_selection(self, event):
        if self.cur_index is None:
            return
        index = self.nearest(event.y)
        if index < self.cur_index:
            value = self.get(index)
            self.delete(index)
            self.insert(index + 1, value)
            self.cur_index = index
        elif index > self.cur_index:
            value = self.get(index)
            self.delete(index)
            self.insert(index - 1, value)
            self.cur_index = index


class PDFPageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF 페이지 상세 편집기")
        self.root.geometry("600x600")

        self.page_data = []

        btn_frame = tk.Frame(root, pady=10)
        btn_frame.pack(fill=tk.X)

        tk.Button(
            btn_frame,
            text="파일 불러오기 (+)",
            command=self.add_files,
            bg="#e1f5fe",
        ).pack(side=tk.LEFT, padx=10)
        tk.Button(
            btn_frame,
            text="선택 페이지 삭제 (-)",
            command=self.remove_selected,
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            btn_frame,
            text="초기화",
            command=self.clear_all,
        ).pack(side=tk.LEFT, padx=5)

        list_frame = tk.Frame(root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = DraggableListbox(
            list_frame,
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 10),
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        tk.Label(
            root,
            text="💡 팁: 각 '페이지'를 드래그하여 순서를 섞으세요. (여러 파일의 페이지를 섞을 수 있습니다)",
            fg="gray",
        ).pack(pady=5)

        action_frame = tk.Frame(root, pady=15)
        action_frame.pack(fill=tk.X)
        tk.Button(
            action_frame,
            text="새로운 PDF로 저장하기",
            command=self.save_pdf,
            bg="#4caf50",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2,
        ).pack(fill=tk.X, padx=20)

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="PDF 파일 선택",
            filetypes=[("PDF Files", "*.pdf")],
        )
        if not files:
            return

        for file_path in files:
            try:
                reader = PdfReader(file_path)
                file_name = os.path.basename(file_path)
                total_pages = len(reader.pages)

                for i in range(total_pages):
                    display_text = f"[{file_name}] - {i + 1}페이지"
                    page_info = {
                        "path": file_path,
                        "page_index": i,
                        "display_text": display_text,
                    }
                    self.page_data.append(page_info)
                    self.listbox.insert(tk.END, display_text)
            except Exception as exc:
                messagebox.showerror(
                    "오류",
                    f"{file_path}를 읽는 중 오류 발생:\n{exc}",
                )

    def remove_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            return

        index = selection[0]
        self.listbox.delete(index)
        del self.page_data[index]

    def clear_all(self):
        self.listbox.delete(0, tk.END)
        self.page_data = []

    def save_pdf(self):
        if not self.page_data:
            messagebox.showwarning("경고", "저장할 페이지가 없습니다.")
            return

        save_path = filedialog.asksaveasfilename(
            title="저장",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
        )
        if not save_path:
            return

        writer = PdfWriter()
        opened_files = {}

        try:
            current_list_items = self.listbox.get(0, tk.END)
            temp_data_pool = self.page_data.copy()
            final_pages = []

            for item_text in current_list_items:
                for i, data in enumerate(temp_data_pool):
                    if data["display_text"] == item_text:
                        final_pages.append(data)
                        temp_data_pool.pop(i)
                        break

            for page_info in final_pages:
                path = page_info["path"]
                idx = page_info["page_index"]

                if path not in opened_files:
                    opened_files[path] = PdfReader(path)

                writer.add_page(opened_files[path].pages[idx])

            writer.write(save_path)
            messagebox.showinfo("성공", "파일이 저장되었습니다!")
        except Exception as exc:
            messagebox.showerror(
                "오류",
                f"저장 중 문제가 발생했습니다:\n{exc}",
            )
        finally:
            writer.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFPageEditorApp(root)
    root.mainloop()
