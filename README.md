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

3. Click **파일 추가 (+)** to add PDFs.
4. Drag items in the list to adjust the merge order.
5. Use **PDF 병합 및 저장** to choose an output path and merge.

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
