from mec import Report, Scraper, ReportWatcher
import sys
import os
import csv

commiteeurl = "https://mec.mo.gov/mec/Campaign_Finance/CommInfo.aspx"


def reporthandler(report):
    # print("Found a report: {}".format(report))
    with open("out.csv", "a") as outfile:
        writer = csv.DictWriter(
            outfile, fieldnames=["name", "address", "employer", "amount", "date", "agg"]
        )
        writer.writerows(report.contributions)


typelookup = {
    "": "15 DAYS AFTER CAUCUS NOMINATION",
    "Quarterly Report": "COMMITTEE QUARTERLY REPORT",
    "8 Day Before": "8 DAYS BEFORE",
    "30 Day After": "30 DAYS AFTER ELECTION",
    "": "TERMINATION",
    "": "SEMIANNUAL DEBT REPORT",
    "": "ANNUAL SUPPLEMENTAL",
    "": "15 DAYS AFTER PETITION DEADLINE",
    "40 Day Before": "OTHER",
}
del typelookup[""]


def rowtofilename(row):
    s = []
    s.append(row["date"].replace("/", "-"))
    if "AMENDED" in row["name"]:
        s.append("AMENDED")
    for keyphrase, type in typelookup.items():
        if keyphrase in row["name"]:
            break
        type = "OTHER"
    if type == "COMMITTEE QUARTERLY REPORT":
        for month in ["January", "April", "July", "October"]:
            if month in row["name"]:
                s.append(month)
    s.append(type.title())
    if row["name"].split()[-2] == "-":
        s.append("- {}".format(row["name"][-1].replace("/", "-")))
    return os.path.join(" ".join(s) + ".pdf")


MECIDs = [
    "C141317",  # Lucas
    "C141272",  # Hall
    "C161413",  # O'Neill
    "C141517",  # Loar
    "C141292",  # Fowler
    "C071015",
    "C101509",
    "C111170",  # Ellington
    "C180541",  # Robinson
    "C151034",  # Shields
    "C180359",  # Bunch
    "C141530",  # Barnes
    "C180188",
    "C190769",  # Parks-Shaw
    "C180601",  # Bough
    "C091059",  # Mcmanus
]

watcher = ReportWatcher("~/Downloads")

watcher = ReportWatcher("/home/jaz/Downloads/reports/oldreports/C141317")

instructions = """PLEASE DO THE FOLLOWING:
	1. Go to {}
	2. Click the year {}
	3. Click the link that says {}
	4. Download the PDF"""

for MECID in MECIDs:
    MECIDpath = os.path.join("reports", MECID)
    if not os.path.exists(MECIDpath):
        os.makedirs(MECIDpath)
    url = "{}?MECID={}".format(commiteeurl, MECID)
    scraper = Scraper(MECID)
    for row in scraper:
        rowpath = os.path.join(MECIDpath, rowtofilename(row))
        if os.path.isfile(rowpath):
            reporthandler(Report.from_file(rowpath))
            continue
        print(instructions.format(url, scraper.year, row["ID"]))
        for reportpath in watcher:
            with open(reportpath, "rb") as f:
                bytes = f.read()
            report = Report.from_bytes(bytes)
            reportpath = os.path.join(MECIDpath, report.filename)
            with open(reportpath, "wb") as f:
                f.write(bytes)
            # print('------\n{}\n{}\n------'.format(reportpath, rowpath))
            if reportpath == rowpath:
                reporthandler(report)
                break
