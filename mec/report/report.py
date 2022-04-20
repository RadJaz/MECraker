from .utils import *
import fitz
import os
from datetime import datetime, timedelta
from .page_mods import *
from openpyxl import Workbook

_reporttypes = [
    "15 DAYS AFTER CAUCUS NOMINATION",
    "COMMITTEE QUARTERLY REPORT",
    "8 DAYS BEFORE",
    "30 DAYS AFTER ELECTION",
    "TERMINATION",
    "SEMIANNUAL DEBT REPORT",
    "ANNUAL SUPPLEMENTAL",
    "15 DAYS AFTER PETITION DEADLINE",
    "OTHER",
]

_typelookup = {
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
del _typelookup[""]


class Report:
    def __init__(self, doc):
        self.doc = doc
        self.validate()

    @classmethod
    def from_file(cls, path: str):
        with open(path, "rb") as f:
            if f.read(4) != b"%PDF":
                raise InvalidReport()
            obj = cls.from_bytes(b"%PDF" + f.read())
            obj.path = path
            return obj

    def move(self, to_path: str):
        os.rename(self.path, to_path)
        self.path = to_path

    @classmethod
    def from_bytes(cls, bytes):
        if bytes[:4] != b"%PDF":
            raise InvalidReport()
        doc = fitz.open(stream=bytes, filetype="pdf")
        r = cls(doc)
        return r

    def validate(self):
        if self.doc.needsPass:
            raise InvalidReport()
        if self.doc.metadata["creator"] != "Toolkit http://www.activepdf.com":
            raise InvalidReport()

    def contributions(self):
        for page in self["cl"]:
            for row in "abcde":
                contribution = self.blankContribution()
                col5 = page["5" + row]
                if not col5:
                    continue
                contribution["amount"] = float(col5.replace(",", ""))
                col4lines = page["4" + row].splitlines()
                for line in col4lines:
                    if "/" in line:
                        contribution["date"] = line
                    elif "." in line:
                        contribution["agg"] = float(line.replace(",", ""))
                col3lines = page["3" + row].splitlines()
                contribution["donor"] = col3lines[0]
                contribution["address"] = " ".join(col3lines[1:3])
                if len(col3lines) > 3:
                    contribution["title"] = " ".join(col3lines[3:])
                if " -- " in contribution["title"]:
                    contribution["employer"], contribution["title"] = contribution[
                        "title"
                    ].split(" -- ")
                yield contribution
        for page in self["contributions"]:
            for row in "abcdefgh":
                contribution = self.blankContribution()
                col5 = page["5" + row]
                if not col5:
                    continue
                contribution["amount"] = float(col5.replace(",", ""))
                col4lines = page["4" + row].splitlines()
                for line in col4lines:
                    if "/" in line:
                        contribution["date"] = line
                    elif "." in line:
                        contribution["agg"] = float(line.replace(",", ""))
                col3lines = page["3" + row].splitlines()
                contribution["donor"] = col3lines[0]
                contribution["address"] = " ".join(col3lines[1:3])
                if len(col3lines) > 3:
                    contribution["title"] = " ".join(col3lines[3:])
                if " -- " in contribution["title"]:
                    contribution["employer"], contribution["title"] = contribution[
                        "title"
                    ].split(" -- ")
                yield contribution

    def expenditures(self):
        for page in self["100+"]:
            for row in range(1, 16):
                row = str(row)
                expenditure = self.blankExpenditure()
                col_d = page[row + "d"]
                if not col_d:
                    continue
                expenditure["amount"] = float(col_d.replace(",", ""))
                expenditure["name"], expenditure["address"] = page[row + "a"].split(
                    "\n", 1
                )
                expenditure["date"] = page[row + "b"]
                expenditure["purpose"] = page[row + "c"]
                if page[row + " PAID"] == page[row + " INCURRED"]:
                    raise Exception("Can't detemine if expense was paid.")
                if page[row + " PAID"]:
                    expenditure["paid"] = True
                yield expenditure
        for page in self["under100"]:
            for row in range(1, 23):
                row = str(row)
                if not page[row + "b"]:
                    continue
                expenditure = self.blankExpenditure()
                expenditure["purpose"] = page[row + "a"]
                expenditure["amount"] = float(page[row + "b"].replace(",", ""))
                yield expenditure
        for page in self["ec"]:
            for row in "ab":
                if not page["4" + row]:
                    continue
                expenditure = self.blankExpenditure()
                expenditure["purpose"] = page["3" + row]
                expenditure["amount"] = float(page["4" + row].replace(",", ""))
                yield expenditure
            for row in "abc":
                expenditure = self.blankExpenditure()
                col11 = page["11" + row]
                if not col11:
                    continue
                expenditure["amount"] = float(col11.replace(",", ""))
                expenditure["name"], expenditure["address"] = page["8" + row].split(
                    "\n", 1
                )
                expenditure["date"] = page["9" + row]
                expenditure["purpose"] = page["10" + row]
                yield expenditure

    def blankContribution(self):
        return {
            "committee": self["cover"]["2"],
            "candidate": self["cover"]["14"].splitlines()[0],
            "election": self["cover"]["11"],
            "donor": "",
            "address": "",
            "employer": "",
            "title": "",
            "amount": 0.0,
            "date": "",
            "agg": 0.0,
        }

    def blankExpenditure(self):
        return {
            "committee": self["cover"]["2"],
            "candidate": self["cover"]["14"].splitlines()[0],
            "name": "",
            "address": "",
            "date": "",
            "purpose": "",
            "amount": 0.0,
            "paid": False,
        }

    def __str__(self):
        s = []
        s.append(self.MECID)
        if self.AMENDED:
            s.append("AMENDED")
        if self.type == "COMMITTEE QUARTERLY REPORT":
            s.append(["January", "April", "July", "October"][self.quarter])
        s.append(self.type.title())
        if self["cover"]["11"]:
            s.append("- {}".format(self["cover"]["11"]))
        return " ".join(s)

    def __getattr__(self, attr):
        if attr == "type":
            cover = self["cover"]
            types = [type for type in _reporttypes if cover[type] == True]
            if "TERMINATION" in types:
                types.remove("TERMINATION")
            if len(types) == 0:
                raise Exception("No type found")
            if len(types) > 1:
                raise Exception("Found more than one type")
            self.type = types[0]
            return self.type
        if attr == "AMENDED":
            self.AMENDED = self["cover"]["AMMENDING PREVIOUS REPORT DATED"]
            return self.AMENDED
        if attr == "quarter":
            quarters = [
                self["cover"][q] for q in ["Jan 15", "Apr 15", "Jul 15", "Oct 15"]
            ]
            qcount = len([q for q in quarters if q])
            if qcount == 0:
                raise Exception("No quarter found")
            if qcount > 1:
                raise Exception("Found more than one quarter")
            self.quarter = quarters.index(True)
            return self.quarter
        if attr == "MECID":
            self.MECID = self["cover"]["MECID"]
            return self.MECID
        if attr == "startdate" or attr == "enddate":
            lines = self["cover"]["13"].splitlines()
            self.startdate = datetime.strptime(lines[0], "%m/%d/%Y")
            self.enddate = datetime.strptime(lines[1], "%m/%d/%Y")
            if self.type == "COMMITTEE QUARTERLY REPORT":
                if self.startdate < self.enddate.replace(
                    day=1, month=self.enddate.month - 2
                ):
                    self.startdate = self.enddate.replace(
                        day=1, month=self.enddate.month - 2
                    )
            if attr == "startdate":
                return self.startdate
            if attr == "enddate":
                return self.enddate
        if attr == "filed":
            self.filed = datetime.strptime(self["cover"]["1"], "%m/%d/%Y")
            return self.filed
        raise AttributeError

    def __getitem__(self, item):
        if item in self.doc.better_toc():
            pages = [self.doc[number] for number in self.doc.better_toc()[item]]
            for page in pages:
                page.type = item
            if item in ["cover", "summary"]:
                return pages[0]
            return pages
        raise KeyError('"{}"'.format(item))

    def matchesrow(self, row):
        if self.AMENDED != ("AMENDED" in row["name"]):
            return False
        date = datetime.strptime(row["date"], "%m/%d/%Y")
        if self.filed != date:
            return False
        for keyphrase, type in _typelookup.items():
            if keyphrase in row["name"]:
                break
            type = "OTHER"
        if type != self.type and type != "OTHER":
            return False
        if (
            type == "COMMITTEE QUARTERLY REPORT"
            and ["January", "April", "July", "October"][self.quarter] not in row["name"]
        ):
            return False
        return True

    def to_excel(self, path):
        wb = Workbook()
        contrib_sheet = wb.active
        contrib_sheet.title = "Contributions"
        header = ["donor", "address", "employer", "title", "amount", "date", "agg"]
        contrib_sheet.append(header)
        header = {k: v + 1 for v, k in enumerate(header)}
        for row in self.contributions():
            row = {header[k]: v for k, v in row.items() if k in header}
            contrib_sheet.append(row)
        contrib_sheet.auto_filter.ref = contrib_sheet.dimensions
        expend_sheet = wb.create_sheet(title="Expenditures")
        header = ["name", "address", "date", "purpose", "amount", "paid"]
        expend_sheet.append(header)
        header = {k: v + 1 for v, k in enumerate(header)}
        for row in self.expenditures():
            row = {header[k]: v for k, v in row.items() if k in header}
            expend_sheet.append(row)
        expend_sheet.auto_filter.ref = expend_sheet.dimensions
        wb.save(path)


class InvalidReport(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "The Report could not be created because an invalid pdf was used."


fitz.Document.better_toc = better_toc
