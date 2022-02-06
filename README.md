# MECraker

MECraker is a set of python tools for collecting campaign finance data from the Missouri Ethics Commision website.

As a program, MECraker can compile donation records and place the records in a spreadsheet for further analysis.

As a library, MECraker can be used to easily parse documents filed with the MEC.

## Dependencies

- Python 3
- [MuPDF](https://mupdf.com/releases/index.html)

### PIP module dependecies

- requests
- PyMuPDF

## Use

To use as a program:

`python3 -m mec run`

MECraker will guide you through how to download the documents. By default, MECraker will watch your `Downloads/` folder for any recently downloaded documents. It will process these documents, cache them in `reports/` and store the data as `.csv` files in `csvs/`.

To generate reference documents:

`python3 -m mec ref {seqno,fields}`

This will generate a reference pdf in the current directory. The seqno reference document is useful for creating templates in the `templates/` directory. The fields reference document is useful for confirming the template. It shows the which area of a page data will be collected for a given variable.
