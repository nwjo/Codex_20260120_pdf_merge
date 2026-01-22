import io
import os
import tkinter as tk
from tkinter import filedialog, messagebox

import fitz
from PIL import Image, ImageTk
from pypdf import PdfReader, PdfWriter


class DraggableListbox(tk.Listbox):
    """드래그 앤 드롭 및 데이터 동기화 리스트박스"""

    def __init__(self, master, data_ref=None, on_select_callback=None, **kw):
        super().__init__(master, **kw)
        self.bind("<Button-1>", self.set_current)
        self.bind("<B1-Motion>", self.shift_selection)
        self.bind("<<ListboxSelect>>", self.on_select)
        self.cur_index = None
        self.data_ref = data_ref
        self.on_select_callback = on_select_callback

    def set_current(self, event):
        self.cur_index = self.nearest(event.y)

    def shift_selection(self, event):
        new_index = self.nearest(event.y)
        if new_index < 0:
            return
        if new_index != self.cur_index:
            text_val = self.get(new_index)
            self.delete(new_index)
            self.insert(self.cur_index, text_val)

            if self.data_ref:
                self.data_ref[new_index], self.data_ref[self.cur_index] = (
                    self.data_ref[self.cur_index],
                    self.data_ref[new_index],
                )

            self.cur_index = new_index
            self.selection_clear(0, tk.END)
            self.selection_set(new_index)
            self.event_generate("<<ListboxSelect>>")

    def on_select(self, event):
        if self.on_select_callback:
            selection = self.curselection()
            if selection:
                self.on_select_callback(selection[0])


class ZoomableImageCanvas(tk.Canvas):
    """이미지 확대/축소 및 이동(Pan)이 가능한 캔버스"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.config(highlightthickness=0, bg="#404040")
        self.original_image = None
        self.shown_image = None
        self.imscale = 1.0

        self.bind("<ButtonPress-1>", self.move_start)
        self.bind("<B1-Motion>", self.move_move)
        self.bind("<MouseWheel>", self.zoom)
        self.bind("<Button-4>", self.zoom)
        self.bind("<Button-5>", self.zoom)

    def set_image(self, pil_image):
        self.original_image = pil_image
        self.imscale = 1.0
        c_width = self.winfo_width()
        c_height = self.winfo_height()
        if c_width > 10 and c_height > 10:
            img_w, img_h = pil_image.size
            ratio = min(c_width / img_w, c_height / img_h)
            self.imscale = ratio if ratio < 1.0 else 1.0
        self.redraw_image()

    def redraw_image(self):
        if not self.original_image:
            return
        new_width = int(self.original_image.width * self.imscale)
        new_height = int(self.original_image.height * self.imscale)
        if new_width < 10 or new_height < 10:
            return

        resized_pil = self.original_image.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS,
        )
        self.shown_image = ImageTk.PhotoImage(resized_pil)

        self.delete("all")
        self.create_image(0, 0, image=self.shown_image, anchor="nw")
        self.config(scrollregion=self.bbox("all"))

    def move_start(self, event):
        self.scan_mark(event.x, event.y)

    def move_move(self, event):
        self.scan_dragto(event.x, event.y, gain=1)

    def zoom(self, event):
        if not self.original_image:
            return
        if event.num == 5 or event.delta < 0:
            scale_multiplier = 0.9
        else:
            scale_multiplier = 1.1
        new_scale = self.imscale * scale_multiplier
        if 0.1 < new_scale < 5.0:
            self.imscale = new_scale
            self.redraw_image()


class PDFMergerCleanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF 병합 심플")
        self.root.geometry("1000x700")

        self.page_data = []

        main_pane = tk.PanedWindow(
            root,
            orient=tk.HORIZONTAL,
            sashwidth=3,
            sashrelief=tk.FLAT,
            bg="#e0e0e0",
        )
        main_pane.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(main_pane)
        main_pane.add(left_frame, minsize=350)

        right_frame = tk.Frame(main_pane, bg="#404040")
        main_pane.add(right_frame, minsize=400)

        btn_frame = tk.Frame(left_frame, pady=10)
        btn_frame.pack(fill=tk.X)

        tk.Button(
            btn_frame,
            text="📂 파일 추가",
            command=self.add_files,
            bg="#2196F3",
            fg="white",
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            btn_frame,
            text="❌ 삭제",
            command=self.remove_selected,
        ).pack(side=tk.LEFT, padx=2)
        tk.Button(
            btn_frame,
            text="🧹 초기화",
            command=self.clear_all,
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame,
            text="💾 저장",
            command=self.save_pdf,
            bg="#4CAF50",
            fg="white",
        ).pack(side=tk.RIGHT, padx=5)
        tk.Button(
            btn_frame,
            text="▼",
            command=self.move_down,
        ).pack(side=tk.RIGHT, padx=2)
        tk.Button(
            btn_frame,
            text="▲",
            command=self.move_up,
        ).pack(side=tk.RIGHT, padx=2)

        list_scroll = tk.Scrollbar(left_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = DraggableListbox(
            left_frame,
            data_ref=self.page_data,
            on_select_callback=self.show_preview,
            selectmode=tk.SINGLE,
            yscrollcommand=list_scroll.set,
            font=("Consolas", 10),
        )
        self.listbox.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
            padx=5,
            pady=(0, 5),
        )
        list_scroll.config(command=self.listbox.yview)

        self.canvas = ZoomableImageCanvas(right_frame)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_text(300, 300, text="[미리보기]", fill="white", justify="center")

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="파일 선택",
            filetypes=[("지원 파일", "*.pdf *.jpg *.jpeg *.png *.bmp")],
        )
        if not files:
            return
        for file_path in files:
            ext = os.path.splitext(file_path)[1].lower()
            fname = os.path.basename(file_path)
            try:
                if ext == ".pdf":
                    reader = PdfReader(file_path)
                    for i in range(len(reader.pages)):
                        self.page_data.append(
                            {
                                "type": "pdf",
                                "path": file_path,
                                "page_index": i,
                                "reader": reader,
                            }
                        )
                        self.listbox.insert(tk.END, f"[PDF] {fname} - {i + 1}p")
                elif ext in {".jpg", ".jpeg", ".png", ".bmp"}:
                    self.page_data.append(
                        {"type": "image", "path": file_path, "page_index": None}
                    )
                    self.listbox.insert(tk.END, f"[IMG] {fname}")
            except Exception as exc:
                messagebox.showerror("에러", str(exc))

    def show_preview(self, index):
        if index >= len(self.page_data):
            return
        item = self.page_data[index]
        pil_image = None
        try:
            if item["type"] == "image":
                pil_image = Image.open(item["path"])
            elif item["type"] == "pdf":
                doc = fitz.open(item["path"])
                pix = doc.load_page(item["page_index"]).get_pixmap(dpi=150)
                mode = "RGBA" if pix.alpha else "RGB"
                pil_image = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
                doc.close()
            if pil_image:
                self.canvas.set_image(pil_image)
        except Exception:
            pass

    def remove_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        for index in reversed(selection):
            self.listbox.delete(index)
            del self.page_data[index]
        self.canvas.delete("all")

    def clear_all(self):
        self.listbox.delete(0, tk.END)
        self.page_data.clear()
        self.canvas.delete("all")

    def move_up(self):
        self._move(-1)

    def move_down(self):
        self._move(1)

    def _move(self, offset):
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        new_index = index + offset
        if 0 <= new_index < len(self.page_data):
            self.page_data[index], self.page_data[new_index] = (
                self.page_data[new_index],
                self.page_data[index],
            )
            text = self.listbox.get(index)
            self.listbox.delete(index)
            self.listbox.insert(new_index, text)
            self.listbox.selection_set(new_index)
            self.show_preview(new_index)

    def save_pdf(self):
        if not self.page_data:
            return
        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
        )
        if not save_path:
            return
        writer = PdfWriter()
        try:
            for data in self.page_data:
                if data["type"] == "pdf":
                    writer.add_page(data["reader"].pages[data["page_index"]])
                elif data["type"] == "image":
                    with Image.open(data["path"]) as img:
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        buffer = io.BytesIO()
                        img.save(buffer, format="PDF")
                        buffer.seek(0)
                        writer.add_page(PdfReader(buffer).pages[0])
            writer.write(save_path)
            messagebox.showinfo("완료", "성공적으로 저장되었습니다!")
        except Exception as exc:
            messagebox.showerror("오류", str(exc))


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFMergerCleanApp(root)
    root.mainloop()
