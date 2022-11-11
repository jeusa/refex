import argparse
import os

import post_processing as pp

def defineArgumentParser():
    parser = argparse.ArgumentParser(description='Postprocessing tool to be used after reference extraction. Creates the 6 csv files: papers, authors, cites, whole_refs, papers_original, papers_original_rearanged')

    parser.add_argument('refs_dir', help='path to the directory containing the files with the extracted references')
    parser.add_argument('refs_info', help='path to the info file for the references')
    parser.add_argument('output_dir', help='optional: output directory for the genereated csv files', nargs='?', default=None)
    parser.add_argument('-r', '--recursive', type=int, help='defines if the input path should be searched recursively, optional: how many levels of subdirectories should be searched', nargs='?', default=False, const=True)
    parser.add_argument('-sn', '--simple_naming', help='set this flag if the names of the original papers are simple and do not contain information about year, country, series, title etc.', action='store_true', default=False)

    return parser.parse_args()

if __name__=='__main__':
    args = defineArgumentParser()

    output_dir = args.output_dir
    if output_dir == None:
        output_dir = os.path.dirname(os.path.normpath(args.refs_info))

    pp.make_tables(args.refs_dir, args.refs_info, save_to_dir=output_dir, simple_naming=args.simple_naming, recursive=args.recursive)
