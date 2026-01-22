# Codex_20260120_pdf_merge

## Usage

1. Install the dependencies:

   ```bash
   pip install pypdf pillow pymupdf
   ```

2. Run the script:

   ```bash
   python pdf_merge.py
   ```

3. Click **📂 파일 추가** to load PDFs or images.
4. Drag items in the list (or use ▲/▼) to reorder pages.
5. Select an item to preview it, then zoom with the mouse wheel and pan by dragging.
6. Use **💾 저장** to pick an output path and save.

## Build a standalone EXE (Windows)

Use PyInstaller to create a single-file executable that runs without Python installed.

1. Install PyInstaller:

   ```bash
   pip install pyinstaller
   ```

2. Build the executable:

   ```bash
   python build_exe.py
   ```

3. Find the output in the `dist/` directory:

   ```text
   dist/pdf_merge.exe
   ```
