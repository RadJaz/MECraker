from .templates import templates, checkbox_templates
from .utils import *
import fitz
import os
from datetime import datetime, timedelta

reporttypes = [
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


class Report:
    def __init__(self, doc):
        self.doc = doc
        self.validate()

    @classmethod
    def from_file(cls, filename: str):
        with open(filename, "rb") as f:
            if f.read(4) != b"%PDF":
                raise InvalidReport()
            return cls.from_bytes(b"%PDF" + f.read())

    @classmethod
    def from_bytes(cls, bytes):
        if bytes[:4] != b"%PDF":
            raise InvalidReport()
        doc = fitz.open(stream=bytes, filetype="pdf")
        r = cls(doc)
        return r

    def validate(self):
        if self.doc.metadata["creator"] != "Toolkit http://www.activepdf.com":
            raise InvalidReport()

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
            types = [type for type in reporttypes if cover[type] == True]
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
            data = self["cover"].parse()
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
        if attr == "contributions":
            contributions = []
            for page in self["c/l"]:
                for row in "abcde":
                    contribution = {
                        "name": "",
                        "address": "",
                        "employer": "",
                        "amount": 0.0,
                        "date": "",
                        "agg": 0.0,
                    }
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
                    contribution["name"] = col3lines[0]
                    contribution["address"] = " ".join(col3lines[1:3])
                    if len(col3lines) > 3:
                        contribution["employer"] = " ".join(col3lines[3:])
                    contributions.append(contribution)
            for page in self["contributions"]:
                for row in "abcdefgh":
                    contribution = {
                        "name": "",
                        "address": "",
                        "employer": "",
                        "amount": 0.0,
                        "date": "",
                        "agg": 0.0,
                    }
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
                    contribution["name"] = col3lines[0]
                    contribution["address"] = " ".join(col3lines[1:3])
                    if len(col3lines) > 3:
                        contribution["employer"] = " ".join(col3lines[3:])
                    contributions.append(contribution)
            self.contributions = contributions
            return self.contributions
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
        for keyphrase, type in typelookup.items():
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


class InvalidReport(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "The Report could not be created because an invalid pdf was used."


def parsepage(page: fitz.Page):
    try:
        return page.data
    except:
        pass
    template = templates[page.type]
    checkbox_template = checkbox_templates[page.type]
    checkmarks, input, _ = page.get_spans()
    data = {label: "" for label, _ in template.items()}
    data.update({label: False for label, _ in checkbox_template.items()})
    for label, rect in template.items():
        for span in input:
            if rect.contains(get_center(span["bbox"])):
                if data[label]:
                    data[label] += "\n"
                data[label] += span["text"]
    for label, rect in checkbox_template.items():
        for span in checkmarks:
            if rect.contains(get_center(span["bbox"])):
                data[label] = True
    page.data = data


def page_getitem(page, item):
    try:
        return page.data[item]
    except:
        page.parse()
    return page.data[item]


fitz.Page.parse = parsepage
fitz.Page.__getitem__ = page_getitem
fitz.Page.get_spans = get_spans
fitz.Document.better_toc = better_toc
