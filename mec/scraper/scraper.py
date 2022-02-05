import requests
from . import parse as parse
from datetime import date, datetime
import time


commiteeurl = "https://mec.mo.gov/mec/Campaign_Finance/CommInfo.aspx"


class Scraper:
    def __init__(self, mecid):
        self.url = "{}?MECID={}".format(commiteeurl, mecid)

    def __iter__(self):
        year = date.today().year
        while str(year) not in self.buttons:
            year -= 1
        while True:
            if year < 2011:
                break
            if str(year) not in self.buttons:
                break
            rows = self.getrowsbyyear(year)
            # remove any redundant rows
            unique = {}
            for row in reversed(rows):
                name = row["name"].replace("AMENDED ", "")
                if name not in unique or datetime.strptime(
                    row["date"], "%m/%d/%Y"
                ) >= datetime.strptime(unique[name]["date"], "%m/%d/%Y"):
                    unique[name] = row
            rows = list(reversed(unique.values()))
            for row in range(len(rows)):
                rows[row]["year"] = year
            del unique
            for row in rows:
                yield row
            year -= 1

    def __getattr__(self, attr):
        if attr == "info_page":
            r = requests.get(self.url)
            return r.text
        if attr == "reports_page":
            form = parse.getform(self.info_page)
            form = {k: v for k, v in form.items() if k[:2] == "__"}
            form[
                "__EVENTTARGET"
            ] = "ctl00$ctl00$ContentPlaceHolder$ContentPlaceHolder1$lbtnReports"
            form["__EVENTARGUMENT"] = ""
            form["ctl00$ctl00$txtUserName"] = ""
            r = requests.post(self.url, data=form)
            self.form = parse.getform(r.text)
            self.buttons = parse.getbuttons(r.text)
            return r.text
        if attr == "buttons":
            self.reports_page
            return self.buttons
        if attr == "form":
            self.reports_page
            return self.form
        raise AttributeError

    def getrowsbyyear(self, year):
        year = str(year)
        self.form[self.buttons[year] + ".x"] = 1
        self.form[self.buttons[year] + ".y"] = 1
        r = requests.post(self.url, data=self.form)
        self.buttons = parse.getbuttons(r.text)
        self.form = parse.getform(r.text)
        return parse.getrows(r.text)
