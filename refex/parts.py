import re

import util
import search


def get_page_titles(matches, page, italics=None):

    if len(matches) > 0:
        titles = []
        rough_titles = []
        publications = []

        next_inside = False

        for i, m in enumerate(matches):
            next_m_close = False
            rough_t, rough_span, clean_t, clean_span, pub = None, None, None, None, None

            if next_inside: # current match starts inside the previos reference, current match probably not a reference
                if i+1 < len(matches):
                    rough_span = (m.span()[1], matches[i+1].span()[0])
                else:
                    rough_span = (m.span()[1], len(page))
                rough_t = page[rough_span[0] : rough_span[1]]
                clean_t, clean_span = clean_title(rough_t, rough_span, m, page, italics)
                clean_t = 'NO REFERENCE, INSIDE OTHER ' + clean_t
                next_inside = False

            else:
                if i+1 < len(matches): # not the last match on this page

                    between_txt = page[m.span()[1] : matches[i+1].span(1)[0]] # text between current reference, starting after the year, and the next one

                    if between_txt.count('\n') <= 2: # next match is in same line as or next line after the current match
                        following_txt = page[m.span()[1]:]
                        following_lines = following_txt.splitlines(True)
                        rough_t = ''.join(following_lines[:3]) # next 3 lines used as rough title
                        rough_span = (m.span()[1], m.span()[1] + len(rough_t))
                        next_m_close = True
                    else:
                        rough_span = (m.span()[1], matches[i+1].span()[0]) # text to the next match is rough title

                else:
                    rough_span = (m.span()[1], len(page))

                rough_t = page[rough_span[0] : rough_span[1]]

                clean_t, clean_span, pub = clean_title(rough_t, rough_span, m, page, italics, get_publication=True)

            if next_m_close:
                if (clean_span[1] > matches[i+1].span(1)[0]): # cleaned title of current match goes into the next match, next match probably not a reference
                    next_inside = True

                    if i+2 < len(matches):
                        rough_span = (m.span()[1], matches[i+2].span()[0])
                    else:
                        rough_span = (m.span()[1], len(page))

                else:
                    rough_span = (m.span()[1], matches[i+1].span()[0])

                rough_t = page[rough_span[0] : rough_span[1]]
                clean_t, clean_span, pub = clean_title(rough_t, rough_span, m, page, italics, get_publication=True)

            rough_titles.append(rough_t)
            titles.append(clean_t)

            if pub:
                publications.append(pub)
            else:
                publications.append("")

        return titles, rough_titles, publications

    else:
        raise ValueError("Lenght of matches is 0")


def clean_title(rough_title, title_span, match, page, italics=None, get_publication=False):

    t_air_quotes = re.search('"[\s\S]+?"|“[\s\S]+?”|(?<![a-z])\'[\s\S]+?(?!\'[a-zA-Z])\'', rough_title)
    title, s, t_italic_span, aq_it, publication = None, None, None, True, None

    if italics:
        t_italic_span = get_italic_span(title_span, italics)

    if (t_air_quotes != None) & (t_italic_span != None):
        t_aq = t_air_quotes.group(0)
        span_aq = (title_span[0] + t_air_quotes.span()[0], title_span[0] + t_air_quotes.span()[0] + len(t_aq))
        if span_aq[0] < t_italic_span[0]:
            title = t_aq
            s = span_aq
            publication = page[t_italic_span[0] : t_italic_span[1]]
        else:
            title = page[t_italic_span[0] : t_italic_span[1]]
            s = t_italic_span
    elif t_air_quotes:
        title = t_air_quotes.group(0)
        s = (title_span[0] + t_air_quotes.span()[0], title_span[0] + t_air_quotes.span()[0] + len(title))
    elif t_italic_span:
        title = page[t_italic_span[0] : t_italic_span[1]]
        s = t_italic_span

    if s != None: # if italic text or text in quotes is far away from reference start, use split method
        if s[0] - match.span()[1] > 15:
            title, s = None, None

    if title == None:
        aq_it = False
        t_split = rough_title.split(',')

        t_s = t_split.pop(0)
        removed_l = 0

        while (len(t_s.strip()) == 0) & (len(t_split) > 0):
            removed_l = removed_l + len(t_s.strip())
            t_s = t_split.pop(0)

        if len(t_split) > 0:
            removed_l = removed_l + (len(t_s) - len(t_s.lstrip()))
            title = t_s.strip()
            s = (title_span[0] + removed_l, title_span[0] + removed_l + len(t_s))

        else:
            title = 'MISSING '
            s = (title_span[0], title_span[0])


    t_clean = clean(title)

    if len(t_clean) == 0:
        t_clean = 'MISSING '

    elif re.search('Table', t_clean):
        t_clean = 'NO REFERENCE, IS A TABLE ' + t_clean

    elif not re.search('\A[A-Z' + search.reg_sp_up + ']|\A21st|\A20st|\A\d{1,4} [A-Za-z' + search.reg_sp + ']|\A\([A-Z]|\Al\'[A-Z]', t_clean):
        t_clean = 'NO REFERENCE ' + t_clean

    if publication:
        publication = clean(publication)

    if get_publication:
        return t_clean, s, publication

    return t_clean, s


def clean(text):
    clean = re.sub('\.\n|,\n', ' ', text)
    clean = re.sub('-\n', '', text)
    clean = re.sub('\n', ' ', clean)
    clean = re.sub('[“”"]*', '', clean)
    clean = re.sub('\[\d{1,2}\]', '', clean)
    clean = re.sub(' {2,3}', ' ', clean)
    clean = clean.strip()

    if (clean.startswith('.') | clean.startswith(',') | clean.startswith(':')) & (len(clean) > 1):
        if len(clean) > 1:
            clean = clean[1:]
            clean = clean.strip()
        else:
            clean = ''

    if (clean.endswith('.') | clean.endswith(',') | clean.endswith(':')) & (len(clean) > 1):
        if len(clean) > 1:
            clean = clean[:-1]
            clean = clean.strip()
        else:
            clean = ''

    return clean

def get_italic_span(span, italics):

    span_italics = [italic[1] for italic in italics if (italic[1][1] >= span[0]) & (italic[1][1] <= span[1])]

    if len(span_italics) > 0:

        result_span = (span_italics[0][0], span_italics[0][1])

        iter_italics = iter(span_italics)
        prev_span_end = next(iter_italics)[1]

        for it in iter_italics:

            if it[0] - prev_span_end <= 6:
                result_span = (result_span[0], it[1])
                prev_span_end = it[1]

            else:
                break

        return result_span

    else:
        return None


def get_titles(paper, matches, paper_italics=None):

    matches_pp, ref_pages = search.group_matches_per_page(matches)
    titles = []
    rough_titles = []
    publications = []

    for i, p_matches in enumerate(matches_pp):
        page_titles, page_rough = [], []

        if paper_italics:
            page_titles, page_rough, page_pubs = get_page_titles(p_matches, paper[ref_pages[i]], paper_italics[ref_pages[i]])
        else:
            page_titles, page_rough, page_pubs = get_page_titles(p_matches, paper[ref_pages[i]])

        titles.append(page_titles)
        rough_titles.append(page_rough)
        publications.append(page_pubs)

    return util.flatten(titles), util.flatten(rough_titles), util.flatten(publications)



def get_authors(matches):

    authors = []
    names = []

    for m, p, s in matches:
        a = m.group(1)
        n = get_author_names(a)

        if re.search('Source[s]?', a, re.IGNORECASE):
            a = 'NO REFERENCE ' + a

        authors.append(a)
        names.append(n)

    return authors, names


def get_author_names(author):

    names = []

    # example: Pekrun, R.
    reg_name = "([A-Za-z" + search.reg_sp + "-]+)\s?, (([A-Z" + search.reg_sp_up + "]\.\s?){1,3})"
    # example: T. Götz
    reg_name_2 =" (([A-Z" + search.reg_sp_up + "]\.\s?){1,3}) ([A-Za-z" + search.reg_sp + "-]+)"

    # example: Hanushek, Eric A.
    reg_name_3 = "([A-Za-z" + search.reg_sp + "-\s]+\.?)\s?, ([A-Za-z" + search.reg_sp + "-\s]+\.?)"
    # example: Marie Waller
    reg_name_4 = "([A-Za-z" + search.reg_sp + "-\s]+\.?) ([A-Za-z" + search.reg_sp + "-\s]+\.?)"

    author = re.sub("\sand", ",", author)
    first_name = re.search(reg_name, author)

    if first_name:
        names.append((first_name.group(1), first_name.group(2).replace(" ", "")))

        author_leftover = re.sub("\s?et\.? al.", " ", author[first_name.span()[1]:])
        type_1_matches = re.findall(reg_name, author_leftover)
        type_2_matches = re.findall(reg_name_2, author_leftover)

        names_leftover = []

        if len(type_1_matches) > len(type_2_matches):
            names_leftover = [(n[0], n[1].replace(" ", "")) for n in type_1_matches]
        else:
            names_leftover = [(n[2], n[0].replace(" ", "")) for n in type_2_matches]

        names = names + names_leftover
    else:
        first_name  = re.search(reg_name_3, author)

        if first_name:
            names.append((first_name.group(1), first_name.group(2)))

            author_leftover = re.sub("\s?et\.? al.", " ", author[first_name.span()[1]:])
            type_3_matches = re.findall(reg_name_3, author_leftover)
            type_4_matches = re.findall(reg_name_4, author_leftover)

            if len(type_3_matches) > len(type_4_matches):
                names_leftover = [(n[0], n[1].strip()) for n in type_3_matches]
            else:
                names_leftover = [(n[1], n[0].strip()) for n in type_4_matches]

            names = names + names_leftover

            for i, (ln, fn) in enumerate(names):
                first_name = fn.split(" ")
                short = ""

                for n in first_name:
                    if len(n) > 0:
                        short += n[0] + "."

                names[i] = (ln, short)

    for ln, fn in names:
        if (len(ln.split(" ")) > 3) | (len(fn.split(" ")) > 3):
            return []

    return names


def get_years(matches):

    years = []

    for m, p, s in matches:
        y = m.group(2)
        y = re.sub('[\(\)]?', '', y)
        y = y.strip()
        years.append(y)

    return years


def get_pages(matches):

    pages = []

    for m, p, s in matches:
        pages.append(p+1)

    return pages


def get_whole_references(matches, rough_titles):

    whole_refs = []

    for i, m in enumerate(matches):
        whole_refs.append(m[0].group() + rough_titles[i])

    return whole_refs
