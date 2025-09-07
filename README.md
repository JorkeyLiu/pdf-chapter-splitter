# PDF Chapter Splitter

## Project Introduction
`PDF Chapter Splitter` is a Python script designed to automatically split large PDF documents into smaller, manageable chapter files based on the PDF's internal bookmarks (outline) information. This is highly useful for users who need to extract specific chapters from a multi-chapter PDF.

## Features
- **Automatic Chapter Recognition**: Automatically identifies chapters based on the PDF's built-in bookmarks (outline).
- **Precise Page Range Splitting**: Calculates precise page ranges for each chapter based on the start page of its bookmark and the start page of the next bookmark (or the end of the document).
- **Output Management**: Saves each chapter as a separate PDF file.
- **Filename Sanitization**: Automatically cleans illegal characters from bookmark titles to ensure valid filenames.
- **Optional Sequencing**: Optionally adds sequential prefixes like `01_`, `02_` to the split files for easier sorting and management.
- **Flexible Output Directory**: Supports specifying an output directory, or automatically creating a subfolder in the original PDF's directory.

## Installation
This project requires a Python 3.x environment.
Please ensure you have the `PyPDF2` library installed:
```bash
pip install PyPDF2
```

## Usage
### Command Line Usage
```bash
python pdf_chapter_splitter.py <input_pdf_path> [-o <output_directory>] [--no-sequence]
```

**Parameter Description:**
*   `<input_pdf_path>`: **Required**. The full path to the PDF file you want to split.
*   `-o <output_directory>`, `--output_dir <output_directory>`: **Optional**. Specifies the output directory for the split PDF files.
    *   If this parameter is **not specified**, the script will create a new subfolder in the same directory as the `input_pdf_path`. This subfolder will be named after the input PDF file (without its extension), and all split chapter PDFs will be saved into this subfolder.
    *   **Example**: If `my_book.pdf` is in `/path/to/documents/`, and `-o` is not specified, the output directory will be `/path/to/documents/my_book/`.
*   `--no-sequence`: **Optional**. A boolean flag. If this flag is included, the split files will **not** have sequential prefixes. By default, files will be prefixed with sequence numbers.
*   `--level <depth>`: **Optional**. An integer. Specifies the level of bookmarks to process.
    *   `1` (default): Only processes top-level bookmarks.
    *   `2`, `3`, etc.: Processes bookmarks up to the specified level.
    *   `0`: Processes all levels of bookmarks.
    *   When the level is set to `0` or greater than `1`, the output filenames will include the full hierarchical path of the bookmark (e.g., `Chapter 1 - Section 1.1.pdf`).

**Usage Examples:**

1.  **Split `my_book.pdf` to the default directory (a subfolder named `my_book` in the same directory as `my_book.pdf`), with sequence numbers:**
    ```bash
    python pdf_chapter_splitter.py my_book.pdf
    ```

2.  **Split `report.pdf` to a specified directory `/path/to/output/`, with sequence numbers:**
    ```bash
    python pdf_chapter_splitter.py report.pdf -o /path/to/output/
    ```

3.  **Split `document.pdf` to the default directory, but without sequence numbers:**
    ```bash
    python pdf_chapter_splitter.py document.pdf --no-sequence
    ```

4.  **Split `document_with_nested_chapters.pdf` processing all bookmark levels, with hierarchical filenames:**
    ```bash
    python pdf_chapter_splitter.py document_with_nested_chapters.pdf --level 0
    ```

5.  **Split `manual.pdf` processing only the first two levels of bookmarks, with hierarchical filenames for the second level:**
    ```bash
    python pdf_chapter_splitter.py manual.pdf --level 2
    ```

### Importing as a Module
You can also import and use the `split_pdf_by_chapters` function in your own Python scripts:
```python
from pdf_chapter_splitter import split_pdf_by_chapters

# Example: Split a PDF
input_file = "path/to/your/document.pdf"
output_folder = "path/to/save/chapters"
split_pdf_by_chapters(input_file, output_folder, add_sequence=True)
```

## Running Tests
To run the project's unit tests, ensure you have `PyPDF2` installed, then execute:
```bash
python -m unittest test/test_pdf_splitter.py
```

## License

This project is licensed under the MIT License.