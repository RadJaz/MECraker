from mec import Report, InvalidReport, Scraper, ReportWatcher, KCcouncil
import sys
import os
import csv
from datetime import timedelta

commiteeurl = "https://mec.mo.gov/mec/Campaign_Finance/CommInfo.aspx"

instructions = """PLEASE DO THE FOLLOWING:
	1. Go to {}
	2. Click the year {}
	3. Click the link that says {}
	4. Download the PDF"""
fieldnames = ["name", "address", "employer", "amount", "date", "agg"]

for member in KCcouncil:
    memberpath = os.path.join("csvs", member + ".csv")
    if not os.path.exists("csvs"):
        os.makedirs("csvs")
    with open(memberpath, "w") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
    for MECID in KCcouncil[member]:
        MECIDpath = os.path.join("reports", MECID)
        lastreport = None
        scraper = Scraper(MECID)
        for row in scraper:
            if (
                "LIMITED ACTIVITY" in row["name"].upper()
                or row["name"].upper() == "TERMINATION"
            ):
                continue
            yearpath = os.path.join(MECIDpath, str(row["year"]))
            if not os.path.exists(yearpath):
                os.makedirs(yearpath)
            reportpath = os.path.join(yearpath, row["ID"])
            if os.path.isfile(reportpath):
                report = Report.from_file(reportpath)
                print(reportpath)
            else:
                print(instructions.format(scraper.url, row["year"], row["ID"]))
                for report in ReportWatcher("~/Downloads"):
                    if report.MECID == MECID and report.matchesrow(row):
                        report.move(reportpath)
                        break
            if lastreport:
                if lastreport.enddate < report.enddate:
                    raise Exception("out of order")
            lastreport = report
            with open(memberpath, "a") as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writerows(report.contributions)
