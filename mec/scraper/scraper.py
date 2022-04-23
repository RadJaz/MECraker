import requests
from . import parse as parse
from datetime import date, datetime
import time


class Scraper:
    prefix = "ctl00$ctl00$ContentPlaceHolder$ContentPlaceHolder1$"

    def submit_form(self, button="", form={}):
        form = {self.prefix + k.replace(self.prefix, ""): v for k, v in form.items()}
        if button:
            form["__EVENTTARGET"] = self.prefix + "lbtn" + button
        form = self.form | form
        self.text = _downloader.post(self.url, data=form).text
        self.form = parse.getform(self.text)
        return self.text

    def __getattr__(self, attr):
        if attr == "form":
            self.text = _downloader.get(self.url).text
            self.form = parse.getform(self.text)
            return self.form


class SearchScraper(Scraper):
    url = "https://mec.mo.gov/mec/Campaign_Finance/CFSearch.aspx"

    def __init__(self):
        self.form

    def active(self):
        self.submit_form(button="Type")
        text = self.submit_form(
            form={"ddType": "Select All", "ddStatus": "Active", "btnSearch": "Search"}
        )
        return parse.search(self.text)

    def terminated(self):
        self.submit_form(button="Type")
        text = self.submit_form(
            form={
                "ddType": "Select All",
                "ddStatus": "Terminated",
                "btnSearch": "Search",
            }
        )
        return parse.search(self.text)

    def all(self):
        return self.active() + self.terminated()


class MECIDScraper(Scraper):
    url = "https://mec.mo.gov/mec/Campaign_Finance/CommInfo.aspx"

    def __init__(self, mecid):
        self.url = "{}?MECID={}".format(self.url, mecid)

    def __iter__(self):
        self.submit_form(button="Reports")
        for year in self.year_generator():
            if year < 2011:
                break
            rows = parse.getrows(self.text)
            # remove any redundant rows
            unique_rows = {}
            for row in reversed(rows):
                name = row["name"].replace("AMENDED ", "")
                if name not in unique_rows or datetime.strptime(
                    row["date"], "%m/%d/%Y"
                ) >= datetime.strptime(unique_rows[name]["date"], "%m/%d/%Y"):
                    row["year"] = year
                    unique_rows[name] = row
            unique_rows = list(reversed(unique_rows.values()))
            for row in unique_rows:
                yield row

    def year_generator(self):
        year_buttons = parse.get_year_buttons(self.text)
        for year, year_button in year_buttons.items():
            form = {year_button + ".x": 1, year_button + ".y": 1}
            self.submit_form(form=form)
            yield year


class Downloader:
    def __init__(self, t=0):
        self.t = t
        self.lasttime = 0

    def request(self, method, url, data={}):
        tries = 0
        while True:
            now = time.time()
            wait = self.t - (now - self.lasttime)
            if wait > 0:
                time.sleep(wait)
            try:
                r = requests.request(method, url, data=data)
                if not r.ok:
                    raise requests.exceptions.RequestException
                self.lasttime = time.time()
                return r
            except requests.exceptions.RequestException:
                print("ConnectionError. Retrying...")
                tries += 1
                if tries == 5:
                    raise Exception("Too many tries!")
                self.lasttime = time.time()
                continue

    def get(self, url):
        return self.request("get", url)

    def post(self, url, data):
        return self.request("post", url, data)


_downloader = Downloader(t=1)
