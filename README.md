© 2022 [Jeúsa Hamer](https://orcid.org/0000-0001-8562-8806)

Contributer: [Helen Seitzer](https://orcid.org/0000-0003-1918-6637)

Refex was created for the Project "The origins of expertise" of UB Bremen and was supported by the Data Science Center of the University of Bremen (DSC@UB).

# refex
This tool can be used to extract the references of a paper and save them in a csv file. It was developed to be used on OECD papers
specifically and does not work with all kinds of formatting of the references. Supported format example: Falch, T. (2004), Main driving
forces of education expenditures

## Usage
The command-line tool can be found in the directory *executables*. Go into the directory matching your operating system. Then navigate to *refex_build*, which contains the executable and all the files necessary to execute the command-line tool. Use the command-line tool by typing `refex.exe` in Windows or `./refex` in Linux.

**refex** generates a csv file for each paper containing all the extracted references if any are found. The name of the csv file will be the same as the one of the pdf file.

`refex [-h] [-v] [-d] [-ni] [-r [RECURSIVE]] [-mt [MULTI_THREADING]] input_path [output_dir]`

**Positional arguments:**  

  `input_path`            : input path of the paper or the directory  
  `output_dir`            : optional, output directory for the csv file(s) containing the extracted references

**Optional arguments:**  

  `-h, --help`            : show this help message and exit  
  `-v, --verbose`         : print infos during extraction  
  `-d, --directory`       : input path is a directory  
  `-ni, --no_info`        : only when input path is a directory, no file with information about the found references for all papers will be generated  
  `-r [RECURSIVE], --recursive [RECURSIVE]`
                        : only when input path is a directory, defines if path should be searched recursively, optional: how many levels of subdirectories should be searched  
  `-mt [MULTI_THREADING], --multi_threading [MULTI_THREADING]`
                        : only when input path is a directory, extract references in multiple threads to be faster, optional: number of threads, default is 5    

### Example usage
Extract references from one pdf file and print information during extraction using `-v` or `--verbose`. The csv file containing the extracted references will be saved in the same directory as the pdf file when *output_dir* is not specified.

`./refex -v INPUT_PATH_FILE`
________
Extract references from multiple pdf files by setting the directory containing the pdf files as *input_path* and setting the flag `-d` or `--directory`. Print information during extraction using `-v` or `--verbose`. Choose an *output_dir* where the extracted references will be written to. A file called *ref_info.csv* containing details about the success of the reference extraction will also be saved to *output_dir*.

`./refex -v -d INPUT_PATH_DIR OUTPUT_PATH`
________
Extract references from multiple pdf files by setting the directory containing the pdf files as *input_path* and setting the flag `-d` or `--directory`. Print information during extraction using `-v` or `--verbose`. Choose an *output_dir* where the extracted references will be written to. Set the flag `-ni` or `--no_info` for *ref_info.csv* to not be generated. Set the flag `-r` or `--recursive` to search the *input_path* recursively. Set `-r 1` or `--recursive 1` to search only one level of subdirectories for pdf files. Set the flag `-mt` or `--multi_threading` to make the program run in multiple threads to be faster. Set `-mt 3` or `--multi_threading 3` to make the program use 3 threads for execution.

`./refex -v -d -ni INPUT_PATH_DIR OUTPUT_PATH -r 1 -mt 3`

# postpro
This tool uses the extracted references and does some postprocessing to bring them in a more usable format. It is to be used after execution of **refex** since it needs the files created by the reference extraction, namely the csv files containing the extracted references and the *ref_info.csv*.

**postpro** generates 6 csv files, the most important ones being *papers.csv*, *authors.csv* and *cites.csv*. If no *output_dir* is specified, the csv files will be written to the parent directory of the *ref_info.csv*.

## Usage
The command-line tool can be found in the directory *executables*. Go into the directory matching your operating system. Then navigate to *postpro_build*, which contains the executable and all the files necessary to execute the command-line tool. Use the command-line tool by typing `postpro.exe` in Windows or `./postpro` in Linux.

`postpro [-h] [-r [RECURSIVE]] [-sn] refs_dir refs_info [output_dir]`

**Positional arguments:**

  `refs_dir`              : path to the directory containing the files with the extracted references  
  `refs_info`             : path to the info file for the references  
  `output_dir`            : optional, output directory for the generated csv files

**Optional arguments:**

  `-h, --help`            : show this help message and exit  
  `-r [RECURSIVE], --recursive [RECURSIVE]`
                      : defines if the input path should be searched recursively, optional: how many levels of subdirectories should be
                      searched  
  `-sn, --simple_naming`  : set this flag if the names of the original papers are not formated and do not contain information about year, country,
                        series, title etc.

## Example usage

Postprocess references and save the created csv files to the given *output_dir*.

`./postpro INPUT_PATH OUTPUT_PATH`
