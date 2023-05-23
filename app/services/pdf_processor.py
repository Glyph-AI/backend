import pdf2image
from PyPDF2 import PdfReader
try:
    from PIL import Image
except ImportError:
    import Image
import tesserocr
from tesserocr import PyTessBaseAPI
from datetime import datetime


class PdfProcessor():
    def __chunk_generator(self, page_count, chunk_size):
        page_array = list(range(1, page_count+1))
        chunk_ids = [i[0] for i in [page_array[i:i+chunk_size]
                                    for i in range(0, len(page_array), chunk_size)]]
        return chunk_ids

    def process(self, filepath):
        # read pdf in
        # try to read it as a searchable pdf first
        searchable = False
        reader = PdfReader(filepath)
        pages_to_check = 5
        if len(reader.pages) < 5:
            pages_to_check = len(reader.pages)
        for i in range(pages_to_check):
            page = reader.pages[i]
            text = page.extract_text()

            if text != "":
                # we can read this PDF as searchable
                searchable = True
                break

        if searchable:
            print("PROCESSING PDF AS DIGITAL")
            pages = len(reader.pages)
            c_time = datetime.now()
            with open("/temp/output.txt", "w+") as f:
                for i in range(pages):
                    page = reader.pages[i]
                    text = page.extract_text()
                    f.write(text)

            print(f"TIME ELAPSED: {datetime.now() - c_time}")

        else:
            print("PROCESSING PDF AS SCANNED")
            pdf_info = pdf2image.pdfinfo_from_path(filepath)
            pages = pdf_info['Pages']
            print(f"Total Pages: {pages}")
            chunk_size = 10
            chunks = self.__chunk_generator(pages, chunk_size)
            c_time = datetime.now()
            with PyTessBaseAPI() as api:
                with open("/temp/output.txt", "w+") as f:
                    for idx in chunks:
                        start = idx
                        end = idx + (chunk_size - 1)
                        images = pdf2image.convert_from_path(
                            filepath, dpi=100, first_page=start, last_page=end)
                        for image in images:

                            api.SetImage(image)
                            page_text = api.GetUTF8Text()
                            f.write(page_text)

            print(f"TIME ELAPSED: {datetime.now() - c_time}")

        return "/temp/output.txt"
