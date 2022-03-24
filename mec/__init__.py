from .report import Report, InvalidReport
from .scraper import MECIDScraper, SearchScraper
from .watcher import ReportWatcher
from .mecids import *


instructions = """PLEASE DO THE FOLLOWING:
	1. Go to {}
	2. Click the year {}
	3. Click the link that says {}
	4. Download the PDF"""
c_fields = [
    "candidate",
    "election",
    "donor",
    "address",
    "employer",
    "title",
    "amount",
    "date",
    "agg",
]
e_fields = ["candidate", "name", "address", "date", "purpose", "amount", "paid"]


def run(MECIDs, csv_path, watch_path, reports_path):
    import os
    import csv

    if not os.path.exists(csv_path):
        os.makedirs(csv_path)
    c_path = os.path.join(csv_path, ".contributions.tmp")
    e_path = os.path.join(csv_path, ".expenditures.tmp")
    with open(c_path, "w") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=c_fields)
        writer.writeheader()
    with open(e_path, "w") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=e_fields)
        writer.writeheader()
    for MECID in MECIDs:
        lastreport = None
        scraper = MECIDScraper(MECID)
        for row in scraper:
            if (
                "LIMITED ACTIVITY" in row["name"].upper()
                or row["name"].upper().replace("AMENDED ", "") == "TERMINATION"
            ):
                continue
            dirpath = os.path.join(reports_path, MECID, str(row["year"]))
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
            reportpath = os.path.join(dirpath, row["ID"])
            print(reportpath)
            if os.path.isfile(reportpath):
                report = Report.from_file(reportpath)
            else:
                print(instructions.format(scraper.url, row["year"], row["ID"]))
                for report in ReportWatcher(watch_path):
                    if report.MECID == MECID and report.matchesrow(row):
                        report.move(reportpath)
                        break
            if lastreport:
                if lastreport.enddate < report.enddate and report.MECID not in [
                    "C180729",
                    "C190775",
                ]:
                    raise Exception("out of order")
            lastreport = report
            with open(c_path, "a") as outfile:
                writer = csv.DictWriter(outfile, fieldnames=c_fields)
                writer.writerows(report.contributions)
            with open(e_path, "a") as outfile:
                writer = csv.DictWriter(outfile, fieldnames=e_fields)
                writer.writerows(report.expenditures)
    os.replace(c_path, os.path.join(csv_path, "contributions.csv"))
    os.replace(e_path, os.path.join(csv_path, "expenditures.csv"))
