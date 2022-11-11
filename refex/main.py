import argparse

import extraction


def defineArgumentParser():
    parser = argparse.ArgumentParser(description='This tool can be used to extract the references of a paper and save them in a csv file. It was developed to be used on OECD papers specifically and does not work with all kinds of formatting of the references. Supported format example: Falch, T. (2004), Main driving forces of education expenditures')

    parser.add_argument('input_path', help='input path of the paper or the directory')
    parser.add_argument('output_dir', help='optional: output directory for the csv file(s) containing the extracted references', nargs='?', default=None)
    parser.add_argument('-v', '--verbose', help='print infos during extraction', action='store_true', default=False)
    parser.add_argument('-d', '--directory', help='input path is a directory', action='store_true', default=False)
    parser.add_argument('-ni', '--no_info', help='only when input path is a directory, no file with information about the found references for all papers will be generated', action='store_true', default=False)
    parser.add_argument('-r', '--recursive', type=int, help='only when input path is a directory, defines if path should be searched recursively, optional: how many levels of subdirectories should be searched', nargs='?', default=False, const=True)
    parser.add_argument('-mt', '--multi_threading',  type=int, help='only when input path is a directory, extract references in multiple threads to be faster, optional: number of threads, default is 5', nargs='?', default=False, const=True)

    return parser.parse_args()


if __name__=='__main__':
    args = defineArgumentParser()
    if not args.directory:
        extraction.extract_references_file(args.input_path, args.output_dir, print_info=args.verbose)
    else:
        info = 'ref_info.csv'
        if args.no_info:
            info = None

        extraction.extract_references_dir(args.input_path, args.output_dir, print_info=args.verbose, recursive=args.recursive, multi_threading=args.multi_threading, info_csv=info)
