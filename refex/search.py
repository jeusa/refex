import re

import util

# special characters
reg_sp_up = "\u00c0-\u00deĀĂĄĆĈĊČĎĐĒĔĖĘĚĜĞĠĢĤĦĨĪĬĮİĲĴĶĹĻĽĿŁŃŅŇŊŌŎŐŒŔŖŘŚŜŞŠŢŤŦŨŪŬŮŰŲŴŶŸŹŻŽ"
reg_sp = "\u00c0-\u017e"

# author
reg_author = "([\[(]?[A-Z" + reg_sp_up + "][\w" + reg_sp + "]+.*?)"

# year: (1965) or (n.d.) or (1965, march 14) or (14 march 1965)
reg_year = "(\(\s?\d{4}.?\s?\)|\(\s?n.d.\s?\)|\(\s?\d{4},\s?\w+\s?\d{0,2}\s?\)|\(\s?\d{0,2}\s?\w+\s?\d{4}\))"
reg_ay = reg_author + "\n?\s*" + reg_year

# newline, author, (year)
reg_nay = "\n[^A-Z\[(\n]*" + reg_ay

# reference page headers
reg_ref = "(Bibliography|Reference[s]?|Find out more|Notes)"


def find_matches(text):

    matches = []

    for match in re.finditer(reg_nay, text):
        matches.append(match)

    return matches


def find_matches_paper(paper, print_info=True):

    if type(paper) is str:
        raise TypeError("Input was str, expected a list. Try find_matches(text) instead.")

    paper_merged = util.merge_paper(paper)

    # List of tupel of all matches found in a paper
    # (match object, the page they are on, their span on the whole paper)
    matches = []

    paper_iter = re.finditer(reg_nay, paper_merged)

    for i, page in enumerate(paper):

        for match in re.finditer(reg_nay, page):
            paper_span = next(paper_iter).span()
            matches.append((match, i, paper_span))

    if print_info:
        print(len(matches), "matches found")

    if len(matches) == 0:
        raise ValueError("No references could be found")

    return matches


def approve_matches(paper, matches, print_info=True):

    # List of matches, that are on a page that lists references.
    # All prior found matches are looked at and added to this list if approved.
    matches_appr = []

    found_ref_page = False

    prev_distance = 800
    m_per_page = 8

    for m, p, s in matches:
        on_ref_page = after_ref_page_header(paper[p], m, 200)

        if on_ref_page:
            matches_appr.append((m, p, s))
            found_ref_page = True

        else:
            if (len(matches_appr) > 0) & found_ref_page :

                prev_match = matches_appr[-1]

                if prev_match[1] == p:  # previous match on same page

                    if prev_match[0].span()[1] >= m.span()[0] - prev_distance:
                        matches_appr.append((m, p, s))

                    elif count_matches_per_page(matches, p) >= m_per_page:
                        matches_appr.append((m, p, s))

                    else:
                        found_ref_page = False

                elif prev_match[1] == p-1:  # previous match on previous page

                    if -len(paper[p-1]) + prev_match[0].span()[1] >= m.span()[0] - prev_distance:
                        matches_appr.append((m, p, s))

                    elif count_matches_per_page(matches, p) >= m_per_page:
                        matches_appr.append((m, p, s))

                    else:
                        found_ref_page = False

                else:
                    found_ref_page = False

    if print_info:
        print(len(matches_appr), "matches approved to be on reference pages")

    if len(matches_appr) == 0:
        raise ValueError("No references could be found and approved")

    return matches_appr


def after_ref_page_header(page, match, distance=None):

    header_match = re.search(reg_ref, page, re.IGNORECASE)

    if header_match:

        if (header_match.span()[1] <= match.span()[0]):
            if distance == None:
                return True

            elif (header_match.span()[1] >= match.span()[0] - distance):
                return True

    return False


def count_matches_per_page(matches, page=None):

    pages = [p for m, p, s in matches]
    matches_pp = []

    for p in set(pages):
        matches_pp.append((p, pages.count(p)))

    if page == None:
        return matches_pp

    else:
        return [n for p, n in matches_pp if p == page][0]


def group_matches_per_page(matches):

    page_matches = []
    matches_pp = []
    pages = []
    prev_page = matches[0][1]

    for m, p, s in matches:
        if p == prev_page:
            page_matches.append(m)
        else:
            matches_pp.append((page_matches.copy()))
            pages.append(prev_page)
            page_matches = []
            page_matches.append(m)
            prev_page = p

    matches_pp.append(page_matches)
    pages.append(prev_page)

    return matches_pp, pages
