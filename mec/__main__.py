from mec import Report, Scraper, ReportWatcher, KCcouncil
import os
import csv

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
        lastreport = None
        scraper = Scraper(MECID)
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
