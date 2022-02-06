def _getbetween(text, str1, str2):
    pos = text.find(str1) + len(str1)
    return text[pos : text.find(str2, pos)]


def getform(text: str) -> dict:
    form = _getbetween(text, "<form", "/form")
    form = form.split("<input")[1:]
    newform = {}
    for input in form:
        id = _getbetween(input, 'id="', '"')
        value = _getbetween(input, 'value="', '"')
        newform[id] = value
    newform = {k: v for k, v in newform.items() if k[:2] == "__"}
    newform["__EVENTTARGET"] = ""
    newform["__EVENTARGUMENT"] = ""
    newform["ctl00$ctl00$txtUserName"] = ""
    return newform


def get_year_buttons(text: str) -> dict:
    tables = text.split('<table id="tablescroll"')[1:]
    tables = [_getbetween(table, ">", "</table>") for table in tables]
    buttons = {}
    for table in tables:
        year = int(_getbetween(table, "<span", "</span>")[-4:])
        button = _getbetween(table, '<input type="image" name="', '"')
        buttons[year] = button
    return buttons


def getrows(text: str) -> list:
    tables = text.split("<table>")[2:]  # first table is the column labels
    tables = [table.split("</table>")[0] for table in tables]
    rows = []
    for table in tables:
        row = {}
        spans = table.split("<span")[1:]
        row["name"], row["date"] = [_getbetween(span, ">", "<") for span in spans]
        row["ID"] = _getbetween(table.split("<a")[1], ">", "</a")
        if "<font" in row["ID"]:
            row["ID"] = _getbetween(row["ID"].split("<font")[1], ">", "</font")
        if "<u" in row["ID"]:
            row["ID"] = _getbetween(row["ID"].split("<u")[1], ">", "</u")
        rows.append(row)
    return rows
