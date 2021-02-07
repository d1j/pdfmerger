#!/usr/bin/env python3

from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
from os import path
from glob import glob
import sys
import subprocess
import argparse


# Returns a directory which specified file is in.
def find_file_directory(file_path):
    last_char_index = file_path.rfind("/")
    if last_char_index == -1:
        return "."
    else:
        return file_path[:last_char_index]


# Finds and returns an output file name that does not exist in the given target dir.
def find_output_file_name(target_dir, output_name):
    i = 0
    out = output_name
    while path.exists(path.join(target_dir, "{}.pdf".format(out))):
        out = output_name + str(i)
        i += 1
    return out


# Finds and returns all file names of specific type in the dirrectory.
def find_files(target_dir, file_ext):
    return glob(path.join(target_dir, "*.{}".format(file_ext)))


# Merges all PDFs in the given directory.
def merge_pdfs(target_dir, output_dir=None):
    # Find pdfs in the given directory.
    pdfs = find_files(target_dir, "pdf")
    merger = PdfFileMerger()

    if len(pdfs) < 1:
        print("ERROR: No pdfs found in the provided directory.")
        sys.exit(1)

    # Merge pdfs.
    print("Found and merging the following pdfs:")
    for pdf in pdfs:
        print(pdf)
        merger.append(pdf)

    if output_dir == None:
        output_dir = target_dir

    # Check if to be writen file does not exist already.
    output_name = find_output_file_name(output_dir, "merged")

    # Output merged pdf.
    output_path = path.join(output_dir, "{}.pdf".format(output_name))
    merger.write(output_path)
    print("Merged pdfs outputed to: {}".format(output_path))
    merger.close()


# Compresses given PDF and outputs it to a new pdf file.
def compress_pdf(target_pdf, output_dir=None):
    # Find output dir if not specified.
    if output_dir == None:
        output_dir = find_file_directory(target_pdf)
    # Find available output file name.
    output_name = find_output_file_name(output_dir, "compressed")

    # Find full output path.
    output_path = path.join(output_dir, "{}.pdf".format(output_name))

    # Run compression.
    ret_code = subprocess.call(
        "python3 ./compress/compress.py -o {} {}".format(output_path, target_pdf), shell=True)
    if ret_code == 0:
        print("Compressed pdf outputed to: {}".format(output_path))


# Splits PDF into two on the given split_page
def split_pdf(target_pdf, split_page, output_dir=None):

    input_pdf = PdfFileReader(open(target_pdf, "rb"))

    if split_page > input_pdf.numPages or split_page < 1:
        print("ERROR: PAGE is out of bounds.")
        sys.exit(1)

    print("Found and spliting {}...".format(target_pdf))

    out_pdf1 = PdfFileWriter()
    out_pdf2 = PdfFileWriter()

    # Build two new pdfs.
    for page in range(split_page):
        out_pdf1.addPage(input_pdf.getPage(page))

    for page in range(split_page, input_pdf.getNumPages()):
        out_pdf2.addPage(input_pdf.getPage(page))

    # Find output dir if not specified.
    if output_dir == None:
        output_dir = find_file_directory(target_pdf)

    # Find available output file name.
    output_name = find_output_file_name(output_dir, "split")

    # Find full output paths.
    output_path1 = path.join(output_dir, "{}_1.pdf".format(output_name))
    output_path2 = path.join(output_dir, "{}_2.pdf".format(output_name))

    # Write newly split pdfs.
    with open(output_path1, 'wb') as file1:
        out_pdf1.write(file1)

    with open(output_path2, 'wb') as file2:
        out_pdf2.write(file2)

    print("PDF succesfully splitted to the following files:\n{}\n{}".format(
        output_path1, output_path2))


def main():
    parser = argparse.ArgumentParser()

    # Create an argument group as the script can do one thing at a time: merge, split or compress.
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-md", "--merge_dir", action="store_true",
                       help="merge all pdfs found in the provided INPUT directory")
    group.add_argument(
        "-s", "--split", action="store_true", help="split INPUT pdf on the given PAGE")
    group.add_argument("-c", "--compress",
                       help="compress INPUT pdf", action="store_true")

    # Input/output arguments. Page argument.
    parser.add_argument(
        "-i", "--input", help="target file/directory", required=True)
    parser.add_argument(
        "-o", "--output", help="if not specified, output defaults to the input file directory", required=False)
    parser.add_argument(
        "-p", "--page", help="page to split the pdf on", type=int)

    # Parse arguments
    args = parser.parse_args()

    # Check if OUTPUT is a valid directory if provided.
    if args.output != None:
        if not path.isdir(args.output):
            print("ERROR: check if OUTPUT is a valid directory.")
            sys.exit(1)

    # Merge
    if args.merge_dir:
        # Check if INPUT is a valid directory.
        if not path.isdir(args.input):
            print("ERROR: check if INPUT is a valid directory.")
            sys.exit(1)
        merge_pdfs(args.input, args.output)
    # Compress
    if args.compress:
        # Check if INPUT file exists.
        compress_pdf(args.input, args.output)
    # Split
    if args.split:
        if not args.page == None:
            split_pdf(args.input, args.page, args.output)
        else:
            print("ERROR: PAGE is not specified.")
            sys.exit(1)


if __name__ == "__main__":
    main()
