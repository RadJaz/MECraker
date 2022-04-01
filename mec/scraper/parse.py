def _getbetween(text, str1, str2):
    pos = text.find(str1) + len(str1)
    return text[pos : text.find(str2, pos)]


def _inner(text):
    open = 0
    s = ""
    for char in text:
        if char == "<":
            open += 1
        elif char == ">":
            open -= 1
        elif not open:
            s += char
    text = s.strip()
    return text


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


def search(text: str) -> list:
    table = text.split("<tr bgcolor=")[2:]
    table = [_getbetween(row, ">", "</tr>") for row in table]
    table = [
        [cell.split("</td>")[0] for cell in row.split("<td>")[1:]] for row in table
    ]
    for row in range(len(table)):
        for cell in range(len(table[row])):
            table[row][cell] = _inner(table[row][cell])
    for row in range(len(table)):
        table[row] = {
            "MECID": table[row][0],
            "committee": table[row][1],
            "candidate": table[row][2],
            "treasurer": table[row][3],
            "deputy treasurer": table[row][4],
            "type": table[row][5],
            "status": table[row][6],
        }
    return table
