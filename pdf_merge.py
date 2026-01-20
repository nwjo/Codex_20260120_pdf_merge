import tkinter as tk
from tkinter import filedialog, messagebox

from pypdf import PdfWriter


class DraggableListbox(tk.Listbox):
    """Listbox that supports drag-and-drop reordering."""

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.bind("<Button-1>", self.set_current)
        self.bind("<B1-Motion>", self.shift_selection)
        self.cur_index = None

    def set_current(self, event):
        """Store the current index on mouse click."""
        self.cur_index = self.nearest(event.y)

    def shift_selection(self, event):
        """Reorder items while dragging the mouse."""
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


class PDFMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF 병합 도구 (순서 변경 가능)")
        self.root.geometry("500x500")

        button_frame = tk.Frame(root, pady=10)
        button_frame.pack(fill=tk.X)

        self.btn_add = tk.Button(
            button_frame,
            text="파일 추가 (+)",
            command=self.add_files,
            bg="#e1f5fe",
        )
        self.btn_add.pack(side=tk.LEFT, padx=10)

        self.btn_remove = tk.Button(
            button_frame,
            text="선택 삭제 (-)",
            command=self.remove_selected,
        )
        self.btn_remove.pack(side=tk.LEFT, padx=5)

        self.btn_clear = tk.Button(
            button_frame,
            text="전체 초기화",
            command=self.clear_all,
        )
        self.btn_clear.pack(side=tk.LEFT, padx=5)

        list_frame = tk.Frame(root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = DraggableListbox(
            list_frame,
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set,
            font=("Arial", 10),
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)

        info_label = tk.Label(
            root,
            text="💡 팁: 목록의 파일을 마우스로 드래그하여 순서를 바꿀 수 있습니다.",
            fg="gray",
        )
        info_label.pack(pady=5)

        action_frame = tk.Frame(root, pady=15)
        action_frame.pack(fill=tk.X)

        self.btn_merge = tk.Button(
            action_frame,
            text="PDF 병합 및 저장",
            command=self.merge_pdfs,
            bg="#4caf50",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2,
        )
        self.btn_merge.pack(fill=tk.X, padx=20)

        self.file_paths = []

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="PDF 파일 선택",
            filetypes=[("PDF Files", "*.pdf")],
        )
        if files:
            for file in files:
                if file not in self.file_paths:
                    self.file_paths.append(file)
                    self.file_listbox.insert(tk.END, file)

    def remove_selected(self):
        selection = self.file_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        file_path = self.file_listbox.get(index)

        self.file_listbox.delete(index)
        if file_path in self.file_paths:
            self.file_paths.remove(file_path)

    def clear_all(self):
        self.file_listbox.delete(0, tk.END)
        self.file_paths = []

    def merge_pdfs(self):
        current_files = self.file_listbox.get(0, tk.END)

        if not current_files:
            messagebox.showwarning("경고", "병합할 파일이 없습니다.")
            return

        save_path = filedialog.asksaveasfilename(
            title="저장할 파일명 입력",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
        )

        if not save_path:
            return

        merger = PdfWriter()
        try:
            for path in current_files:
                merger.append(path)

            merger.write(save_path)
            messagebox.showinfo(
                "완료",
                f"성공적으로 병합되었습니다!\n\n저장 위치:\n{save_path}",
            )
        except Exception as exc:
            messagebox.showerror("오류", f"병합 중 오류가 발생했습니다:\n{exc}")
        finally:
            merger.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFMergerApp(root)
    root.mainloop()
