from PyPDF2 import PdfFileMerger
from os import path
from glob import glob

import pathlib


def find_ext(dr, ext):
    return glob(path.join(dr, "*.{}".format(ext)))


def main():
    pdfs = find_ext(".", "pdf")
    merger = PdfFileMerger()

    for pdf in pdfs:
        merger.append(pdf)

    merger.write("result.pdf")
    merger.close()


if __name__ == "__main__":
    main()
