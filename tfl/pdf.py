from pypdf import PdfReader, PdfWriter
from io import BytesIO

def split_pdf_pages(pdf_obj: BytesIO) -> list[BytesIO]:
    output_files = []
    with PdfReader(pdf_obj) as reader:
        for page_num in range(len(reader.pages)):
            with PdfWriter() as writer:
                writer.add_page(reader.pages[page_num])
                output = BytesIO()
                writer.write(output)
                output.seek(0)
                output_files.append(output)

    return output_files