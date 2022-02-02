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
        url = "{}?MECID={}".format(commiteeurl, MECID)
        lastreport = None
        for row in Scraper(MECID):
            if (
                "LIMITED ACTIVITY" in row["name"].upper()
                or row["name"].upper() == "TERMINATION"
            ):
                continue
            yearpath = os.path.join(MECIDpath, str(row["year"]))
            if not os.path.exists(yearpath):
                os.makedirs(yearpath)
            rowpath = os.path.join(yearpath, row["filename"])
            print(rowpath)
            if os.path.isfile(rowpath):
                report = Report.from_file(rowpath)
            else:
                print(instructions.format(url, row["year"], row["ID"]))
                for reportpath in ReportWatcher("~/Downloads"):
                    report = Report.from_file(reportpath)
                    if report.MECID == MECID and report.matchesrow(row):
                        os.rename(reportpath, rowpath)
                        break
            if lastreport:
                if lastreport.enddate < report.enddate:
                    raise Exception("out of order")
            lastreport = report
            with open(memberpath, "a") as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writerows(report.contributions)
