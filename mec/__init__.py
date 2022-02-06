from .report import Report, InvalidReport
from .scraper import MECIDScraper, SearchScraper
from .watcher import ReportWatcher
from .mecids import *


instructions = """PLEASE DO THE FOLLOWING:
	1. Go to {}
	2. Click the year {}
	3. Click the link that says {}
	4. Download the PDF"""
fieldnames = ["name", "address", "employer", "amount", "date", "agg"]


def run(MECIDs, csv_path, watch_path):
    import os
    import csv

    if not os.path.exists(csv_path):
        os.makedirs(csv_path)
    for member in MECIDs:
        temppath = os.path.join(csv_path, ".temp.csv")
        with open(temppath, "w") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
        for MECID in MECIDs[member]:
            lastreport = None
            scraper = MECIDScraper(MECID)
            for row in scraper:
                if (
                    "LIMITED ACTIVITY" in row["name"].upper()
                    or row["name"].upper() == "TERMINATION"
                ):
                    continue
                dirpath = os.path.join("reports", MECID, str(row["year"]))
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
                    if lastreport.enddate < report.enddate:
                        raise Exception("out of order")
                lastreport = report
                with open(temppath, "a") as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                    writer.writerows(report.contributions)
        memberpath = os.path.join(csv_path, member + ".csv")
        os.rename(temppath, memberpath)
