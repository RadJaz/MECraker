from .. import *

instructions = """PLEASE DO THE FOLLOWING:
    1. Go to {}
    2. Click "Reports"
    3. Click the year {}
    4. Click the link that says {}
    5. Download the PDF"""


def run(MECIDs, csv_path, watch_path, reports_path):
    import os
    import csv

    if not os.path.exists(csv_path):
        os.makedirs(csv_path)
    c_path = os.path.join(csv_path, ".contributions.tmp")
    e_path = os.path.join(csv_path, ".expenditures.tmp")
    if os.path.exists(c_path):
        os.remove(c_path)
    if os.path.exists(e_path):
        os.remove(e_path)
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
            if not os.path.exists(c_path):
                with open(c_path, "w") as outfile:
                    writer = csv.DictWriter(
                        outfile, fieldnames=report.blankContribution().keys()
                    )
                    writer.writeheader()
            if not os.path.exists(e_path):
                with open(e_path, "w") as outfile:
                    writer = csv.DictWriter(
                        outfile, fieldnames=report.blankExpenditure().keys()
                    )
                    writer.writeheader()
            with open(c_path, "a") as outfile:
                writer = csv.DictWriter(
                    outfile, fieldnames=report.blankContribution().keys()
                )
                writer.writerows(report.contributions())
            with open(e_path, "a") as outfile:
                writer = csv.DictWriter(
                    outfile, fieldnames=report.blankExpenditure().keys()
                )
                writer.writerows(report.expenditures())
    os.replace(c_path, os.path.join(csv_path, "contributions.csv"))
    os.replace(e_path, os.path.join(csv_path, "expenditures.csv"))
