import os
import re
import fitz


def read_pdf(path, get_italic=False, print_info=True):

    pdf_pages = []
    pdf_dicts = []

    if print_info:
        print("Reading pdf from", path)
        print("...")

    with fitz.open(path) as pdf:
        for page in pdf:
            pdf_pages.append(page.get_text())

            if get_italic:
                pdf_dicts.append(page.get_text('dict', flags=~fitz.TEXT_PRESERVE_IMAGES))

    if print_info:
        print("Finished reading", len(pdf_pages), "page(s)")

    if get_italic:
        return pdf_pages, get_italics(extract_text_italic_marked(pdf_dicts))

    return pdf_pages


def extract_text_italic_marked(pdf_dicts):

    italic_texts = []
    italics = []
    lines = []
    pdf_pages = []

    for page_no, page in enumerate(pdf_dicts):
        page_italics = []
        page_lines = []

        for block in page['blocks']:
            if block['type'] == 0:  # text block
                for line in block['lines']:

                    cur_line = []
                    for span in line['spans']:

                        text = span['text']

                        if (span['flags'] == 6) & (re.search('italic', span['font'], re.IGNORECASE) != None):
                            italic_texts.append((page_no, span['text']))

                            text = '<italic>' + text + '</italic>'
                            page_italics.append(text)


                        cur_line.append(text)

                    cur_line = ''.join(cur_line)
                    page_lines.append(cur_line)

        lines.append(page_lines)
        pdf_pages.append('\n'.join(page_lines) + '\n')

    return pdf_pages


def get_italics(paper):

    start_tag = len('<italic>')
    end_tag = len('</italic>')
    italics_found = False

    it_matches = []

    for page in paper:
        matches_page = []

        for i, match in enumerate(re.finditer('<italic>([\s\S]+?)</italic>', page)):
            span_start = match.span()[0] - i * (start_tag + end_tag)
            span_end = match.span()[1] - (i+1) * (start_tag + end_tag)

            matches_page.append((match.group(1), (span_start, span_end)))

            italics_found = True

        it_matches.append(matches_page)

    if italics_found:
        return it_matches

    else:
        return None


def flatten(t):
    return [item for sublist in t for item in sublist]


def merge_paper(paper):
    return ''.join(paper[:])


def list_files(directory, suffix='', recursive=True):

    if not directory.endswith(os.sep):
        directory = directory + os.sep

    files = []
    dir_files = os.listdir(directory)

    rec = recursive
    if type(recursive) is int:
        rec = recursive-1

    for f in dir_files:

        if f.lower().endswith(suffix):
            files.append(directory + f)

        elif ((recursive == True) | (recursive >= 1)) & os.path.isdir(directory + f):
            sub_dir_files = list_files(directory + f, suffix, rec)
            files = files + sub_dir_files

    return files
