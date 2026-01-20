# Codex_20260120_pdf_merge

## Usage

1. Install the dependency:

   ```bash
   pip install pypdf
   ```

2. Run the script:

   ```bash
   python pdf_merge.py
   ```

3. Click **파일 불러오기 (+)** to load PDFs and list every page.
4. Drag pages in the list to reorder them across files.
5. Use **새로운 PDF로 저장하기** to pick an output path and save.

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
