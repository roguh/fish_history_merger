# fix_fish_history.py

## Fix some unparseable YAML lines and sort history

```bash
$ ./fix_fish_history.py file1 -o outputfile
```

## Merge N fish history files

They need to be sorted so that fish will parse the output correctly.

```bash
$ ./fix_fish_history.py file1 file2 file3 -o outputfile
```

## Usage

```bash
$ fix_fish_history --help
usage: fix_fish_history.py [-h] [--run-pytests] [--lint] [--verbose]
                           [--nosort] [--noparsefix] [--append]
                           [--out-fname OUT_FNAME]
                           fish_history_files [fish_history_files ...]

Fix or lint a fish_history file in various ways. Unparseable YAML and unsorted
history is detected and fixed. The output should be a valid YAML file.

positional arguments:
  fish_history_files    The fish_history file to fix

options:
  -h, --help            show this help message and exit
  --run-pytests         Just run the unit tests for this script if pytest is
                        installed.
  --lint                Just count the number of fixes, do not actually fix
                        them. This includes number of unsorted history entries
                        and number of YAML parse errors found.
  --verbose             Enable debug logging. This shows YAML parse error
                        details.
  --nosort              Do not sort lines in the history file
  --noparsefix          Do not try to fix parse errors
  --append, -a          Append to the output filename --out-fname do not
                        overwrite
  --out-fname OUT_FNAME, -o OUT_FNAME
                        Write fixed output to this file. Incompatible with
                        --lint

```
