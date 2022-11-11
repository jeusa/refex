import pandas as pd
import os
import re

from threading import Thread

import util
import search
import parts


def search_references(paper, paper_italics=None, print_info=True, remove_false_refs=True):

    try:
        matches_found = search.find_matches_paper(paper, print_info)
        matches_appr = search.approve_matches(paper, matches_found, print_info)

    except:
        if print_info:
            print("References could not be found")
        return

    titles, rough_titles, publications = parts.get_titles(paper, matches_appr, paper_italics)
    authors, names = parts.get_authors(matches_appr)
    years = parts.get_years(matches_appr)
    pages = parts.get_pages(matches_appr)
    whole_refs = parts.get_whole_references(matches_appr, rough_titles)

    refs_l = []

    for i, a in enumerate(authors):
        row = [a, names[i], years[i], titles[i], publications[i], pages[i], whole_refs[i]]
        refs_l.append(row)

    ref_df = pd.DataFrame(refs_l, columns=['authors', 'author_names', 'year', 'title', 'publication', 'page', 'whole_ref'])

    if remove_false_refs:
        ref_df = remove_false_references(ref_df)

    return ref_df


def get_references(path, print_info=True):

    try:
        paper, paper_italics = util.read_pdf(path, get_italic=True, print_info=print_info)

    except Exception as e:
        if print_info:
            print('Could not read pdf')
            print('Exception raised:', e)
        return 0

    else:
        ref_df = search_references(paper, paper_italics, print_info)
        return ref_df


def extract_references_file(input_path, output_dir=None, get_df=False, print_info=True):

    if os.path.isfile(input_path) and input_path.endswith('.pdf'):
        ref_df = get_references(input_path, print_info)
    else:
        print('Input path is not valid')
        print(input_path)
        return

    if output_dir == None:
        output_dir = re.sub('pdf', 'csv', input_path)
    elif os.path.isdir(output_dir):
        if not output_dir.endswith(os.sep):
            output_dir = output_dir + os.sep

        output_dir = output_dir + input_path.split(os.sep)[-1]
        output_dir = re.sub('pdf', 'csv', output_dir)
    else:
        print('Output path is not a directory')
        return

    if isinstance(ref_df, pd.DataFrame):
        ref_df.to_csv(output_dir, index=False)
        if print_info:
            print('Wrote references to', output_dir)
    else:
        if print_info:
            print('Did not write references to csv')

    if get_df:
        return ref_df


def extract_references_dir(input_dir, output_dir=None, recursive=False, info_csv=None, print_info=True, multi_threading=False):

    if os.path.isdir(input_dir):
        if not input_dir.endswith(os.sep):
            input_dir = input_dir + os.sep
    else:
        print('Input path is not a directory')
        return

    info_dir = input_dir
    if output_dir:
        if os.path.isdir(output_dir):
            if not output_dir.endswith(os.sep):
                output_dir = output_dir + os.sep
            info_dir = output_dir
        else:
            print('Output path is not a directory')
            return

    info_path = None
    if info_csv:
        info_path = info_dir + info_csv

    paper_paths = util.list_files(input_dir, suffix='pdf', recursive=recursive)
    papers = []

    for p in paper_paths:
        p_clean = p.replace(input_dir, '')
        papers.append(p_clean)

    papers_df = pd.DataFrame(papers, columns=['paper'])
    papers_df['references_found'] = False
    papers_df['references_count'] = 0
    papers_df['not_readable'] = False

    if multi_threading:

        threads = 5
        if type(multi_threading) is int:
            threads = multi_threading

        if print_info:
            print('Doing multithreading')

        current_threads = []
        index = 0
        papers_n = len(paper_paths)

        while (len(paper_paths) > 0) | (len(current_threads) > 0):

            if (len(current_threads) < threads) & (len(paper_paths) > 0):
                if print_info:
                    print('Starting thread', index+1, 'of', papers_n)
                    print('for pdf:', paper_paths[0])

                extract_thread = extract_references_thread(paper_paths.pop(0), output_dir, index)
                extract_thread.start()
                current_threads.append(extract_thread)

                index = index+1

            if len(current_threads) > 0:
                if not current_threads[0].is_alive():
                    ref_df = current_threads[0].ref_df
                    i = current_threads[0].index
                    papers_df = update_info(papers_df, ref_df, i, info_path)

                    if print_info:
                        print('Finished thread', i+1)

                    current_threads.pop(0)

    else:
        for i, p in enumerate(paper_paths):

            ref_df = extract_references_file(p, output_dir, get_df=True, print_info=print_info)
            papers_df = update_info(papers_df, ref_df, i, info_path)

            if print_info:
                print()

    return papers_df


def update_info(info_df, ref_df, index, write_to=None):
    papers_df = info_df.copy()

    if isinstance(ref_df, pd.DataFrame):
        papers_df.at[index, 'references_found'] = True
        papers_df.at[index, 'references_count'] = ref_df.shape[0]
    elif ref_df == 0:
        papers_df.at[index, 'not_readable'] = True

    if write_to:
        papers_df.to_csv(write_to)

    return papers_df


def remove_false_references(ref_df):
    df = ref_df.copy()

    for i, row in df.iterrows():
        reg_no_ref = "(NO REFERENCE|MISSING)"

        if re.search(reg_no_ref, row['authors'] + row['title']):
            df = df.drop(i)

    return df


class extract_references_thread(Thread):

    def __init__(self, input_path, output_dir, index):
        Thread.__init__(self)
        self.input_path = input_path
        self.output_dir = output_dir
        self.index = index
        self.ref_df = None

    def run(self):
        self.ref_df = extract_references_file(self.input_path, self.output_dir, get_df=True, print_info=False)
