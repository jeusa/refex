import numpy as np
import pandas as pd
import re
import os
import ast


def get_original_papers(ref_info_path, simple_naming=False, save_to=None):
    papers_orig = pd.read_csv(ref_info_path, index_col=0)
    papers_orig = papers_orig.loc[papers_orig["references_found"]]

    papers_orig = papers_orig.rename(columns={"paper": "file_path"})
    papers_orig = papers_orig.drop(columns=["references_found", "not_readable"])

    regex_file = "(\d{4})_([\s\S]*?)_([\s\S]*?)_([\s\S]*?)_([\s\S]*?)_([\s\S]*).pdf"

    papers_orig["file_name"] = ""
    papers_orig["first_title"] = ""
    papers_orig["second_title"] = ""
    papers_orig["year"] = 0
    papers_orig["series"] = ""
    papers_orig["country"] = ""
    papers_orig["other"] = ""

    for paper_id, row in papers_orig.iterrows():

        paper_details = re.search(regex_file, row["file_path"])

        if not simple_naming:
            if not (paper_details):
                papers_orig = papers_orig.drop(paper_id)
            else:
                papers_orig.at[paper_id, "year"] = paper_details.group(1).replace("NA", "0")
                papers_orig.at[paper_id, "country"] = paper_details.group(2).replace("NA", "")
                papers_orig.at[paper_id, "series"] = paper_details.group(3).replace("NA", "")
                papers_orig.at[paper_id, "first_title"] = paper_details.group(4).replace("NA", "")
                papers_orig.at[paper_id, "second_title"] = paper_details.group(5).replace("NA", "")
                papers_orig.at[paper_id, "other"] = paper_details.group(6).replace("NA", "").replace(".pdf", "").replace("-pdf", "")
                papers_orig.at[paper_id, "file_name"] = row["file_path"].split(os.sep)[-1].replace(".pdf", "")

        else:
            papers_orig.at[paper_id, "file_name"] = row["file_path"].split(os.sep)[-1].replace(".pdf", "")

    papers_orig["year"] = papers_orig["year"].astype(int)

    papers_orig = papers_orig.reset_index(drop=True)
    papers_orig["id"] = papers_orig.index
    papers_orig = papers_orig.set_index("id")

    if save_to:
        papers_orig.to_csv(save_to)

    return papers_orig


def rearange_original_papers(orig_papers_df, simple_naming=False, save_to=None):

    papers = orig_papers_df[["first_title", "second_title", "year", "series", "country", "other"]].copy()
    papers["title"] = ""

    if simple_naming:
        papers["title"] = orig_papers_df["file_name"]
    else:
        for i, row in papers.iterrows():
            title = row["series"]

            if len(row["first_title"]) > 0:
                if len(title) > 0:
                    title += ": "
                title += row["first_title"]

            if len(row["second_title"]) > 0:
                if len(row["first_title"]) > 0:
                    title += " - "
                title += row["second_title"]

            if len(row["country"]) > 0:
                if not re.search(row["country"], title):
                    title += " " + row["country"]

            if len(row["other"]) > 0:
                title += ", " + row["other"]

            papers.at[i, "title"] = title

    papers = papers[["title", "year"]].copy()
    papers["authors"] = "OECD"
    papers["author_names"] = ""
    papers["publication"] = ""
    papers["by_oecd"] = True

    if save_to:
        papers.to_csv(save_to)

    return papers


def rearange_ref_file(ref_file_path, index_start):

    refs = pd.read_csv(ref_file_path, converters={1: ast.literal_eval})
    ids = np.arange(index_start, index_start + refs.shape[0])
    authors = pd.DataFrame(columns=["paper_id", "author"])

    whole_refs = refs[["whole_ref"]]
    refs = refs.drop(columns=["page", "whole_ref"])
    refs["by_oecd"] = False
    refs = refs.reindex(columns=["title", "year", "authors", "author_names", "publication", "by_oecd"])

    refs["id"] = ids
    whole_refs["id"] = ids
    refs = refs.set_index("id")
    whole_refs = whole_refs.set_index("id")

    for i, row in refs.iterrows():
        year = re.search("\d{4}", str(row["year"]))
        if year:
             year = year.group()
        else:
             year = 0
        refs.at[i, "year"] = year

        if re.search("OECD", str(row["authors"]) + str(row["publication"]), re.IGNORECASE):
            refs.at[i, "by_oecd"] = True


        cur_authors = []
        if row["author_names"]:
            for author in row["author_names"]:
                cur_authors.append({"paper_id": row.name, "author": author[0] + ", " + author[1]})
        else:
            cur_authors.append({"paper_id": row.name, "author": row["authors"]})

        authors = pd.concat([pd.DataFrame(cur_authors, columns=authors.columns), authors], ignore_index=True)

    return refs, authors.sort_values(by=["paper_id"]), whole_refs


def make_tables(refs_dir, refs_info_file, save_to_dir=None, simple_naming=False, recursive=False, save_papers_to=None, save_refs_to=None, save_cites_to=None, save_authors_to=None, save_orig_to=None):

    if save_to_dir:
        if os.path.isdir(save_to_dir):
            if not save_to_dir.endswith(os.sep):
                save_to_dir += os.sep

            save_papers_to = save_to_dir + "papers.csv"
            save_refs_to = save_to_dir + "whole_refs.csv"
            save_cites_to = save_to_dir + "cites.csv"
            save_orig_to = save_to_dir + "papers_original.csv"
            save_authors_to = save_to_dir + "authors.csv"

        else:
            print("Output path is not a directory.")
            return

    papers_orig = get_original_papers(refs_info_file, simple_naming)
    papers = rearange_original_papers(papers_orig, simple_naming)
    papers_rearanged = papers.copy()

    whole_refs = pd.DataFrame(columns=["id", "whole_ref"])
    whole_refs = whole_refs.set_index("id")

    cites = pd.DataFrame(columns=["paper_id_cites", "paper_id_cited"])

    authors = pd.DataFrame(columns=["paper_id", "author"])

    refs_files = list_files(refs_dir, suffix="csv", recursive=recursive)

    for i, f in enumerate(refs_files):
        print("Adding file ", i+1, " of ", len(refs_files), f)
        file_name = os.path.basename(f)
        file_name = file_name.replace(".csv", "")

        row = papers_orig.loc[papers_orig["file_name"] == file_name]
        if not(row.empty):
            paper_id_cites = row.index.values[0]
            refs, auth, whole = rearange_ref_file(f, papers.shape[0])
            refs_cited = pd.DataFrame({"paper_id_cited": refs.index.to_list()})
            refs_cited["paper_id_cites"] = row.index.values[0]

            papers = pd.concat([papers, refs])
            whole_refs = pd.concat([whole_refs, whole])

            cites = pd.concat([cites, refs_cited])

            authors = pd.concat([auth, authors])

    orig_authors = papers_rearanged[["authors"]].copy().reset_index().rename(columns={"authors": "author", "id": "paper_id"})
    authors = pd.concat([orig_authors, authors])

    cites = cites.sort_values(by=["paper_id_cites"]).reset_index(drop=True)
    authors = authors.sort_values(by=["paper_id"]).reset_index(drop=True)

    if save_papers_to:
        papers.to_csv(save_papers_to)
    if save_cites_to:
        cites.to_csv(save_cites_to, index=False)
    if save_authors_to:
        authors.to_csv(save_authors_to, index=False)
    if save_refs_to:
        whole_refs.to_csv(save_refs_to)
    if save_orig_to:
        papers_orig.to_csv(save_orig_to)
        papers_rearanged.to_csv(save_orig_to.replace(".csv", "") + "_rearanged.csv")

    return papers, cites, authors, whole_refs


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
