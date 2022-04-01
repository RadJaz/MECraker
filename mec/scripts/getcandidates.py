from .. import Scraper
from ..scraper import parse

SearchElection = "https://mec.mo.gov/mec/Campaign_Finance/CF12_SearchElection.aspx"

formitems = [
    "ElectionYear",
    "ElectionDate",
    "PoliticalOffice",
    "Status",
    "PoliticalDistrict",
    "PoliticalSubdivision",
]


def getcandidates(race):
    scraper = Scraper()
    scraper.url = SearchElection
    form = {"ddElectionDate": "-- Select Election --"}
    for formitem in formitems:
        if formitem not in race.keys():
            continue
        form["dd" + formitem] = race[formitem]
        scraper.submit_form(form=form)
    form["btnSearch"] = "Search"
    text = scraper.submit_form(form=form)
    table = parse._getbetween(
        text,
        '<table cellspacing="0" cellpadding="3" id="ContentPlaceHolder_ContentPlaceHolder1_grvElection"',
        "</table>",
    )
    table = table.split("<tr")[2:]
    for row in range(len(table)):
        table[row] = table[row].split("</tr")[0]
        table[row] = table[row].split("<td>")[2:]
        for cell in range(len(table[row])):
            table[row][cell] = parse._inner(table[row][cell])
    results = {}
    for row in table:
        results[row[0]] = {
            "candidate": row[1],
            "party": row[2],
            "office": row[3],
            "status": row[4],
        }
    return results
