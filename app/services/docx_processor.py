import pypandoc

class DocxProcessor():
    def process(self, filepath):
        pypandoc.convert_file(filepath, 'plain', outputfile="/temp/output.txt")

        return "/temp/output.txt"