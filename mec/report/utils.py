pagenames = {
    "EXPENDITURES OF $100 OR LESS BY CATEGORY - SUPPLEMENTAL FORM": "<100",
    "CONTRIBUTIONS AND LOANS RECEIVED": "c/l",
    "CONTRIBUTIONS RECEIVED - SUPPLEMENTAL": "contributions",
    "EXPENDITURES AND CONTRIBUTIONS MADE": "e/c",
    "ITEMIZED EXPENDITURES OVER $100 SUPPLEMENTAL FORM": "100+",
    "COMMITTEE DISCLOSURE REPORT COVER PAGE": "cover",
    "REPORT SUMMARY": "summary",
    "EXPLANATION FOR AMENDED REPORT": "explanation",
    "ADDENDUM STATEMENT": "addendum",
    "INDEPENDENT CONTRACTOR EXPENDITURE": "contractor",
    "DIRECT EXPENDITURE REPORT": "direct",
    "SUPPLEMENTAL LOAN INFORMATION": "supplemental",
    "FUND-RAISING STATEMENT": "fundraising",
    "CONTRIBUTIONS MADE - SUPPLEMENTAL FORM": "",
    "CONTRACTUAL RELATIONSHIP REPORT": "",
    "COMMITTEE TERMINATION STATEMENT": "",
}


def get_spans(page):
    try:
        return page.spans
    except:
        pass
    dict = page.get_text("dict")
    spans = []
    for block in dict["blocks"]:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            if "spans" in line:
                spans += line["spans"]
    page.spans = sort_spans(spans)
    return page.spans


def sort_spans(spans):
    checkmarks = []
    input = []
    form = []
    for span in spans:
        if span["text"] == "\x14":
            checkmarks.append(span)
        elif span["font"] == "Courier":
            input.append(span)
        else:
            form.append(span)
    checkmarks.sort(key=lambda span: (span["bbox"][1], span["bbox"][0]))
    input.sort(key=lambda span: (span["bbox"][1], span["bbox"][0]))
    form.sort(key=lambda span: (span["bbox"][1], span["bbox"][0]))
    return checkmarks, input, form


def get_center(item):
    return ((item[0] + item[2]) / 2, (item[1] + item[3]) / 2)


def sort_drawings(drawings):
    circles = []
    rectangles = []
    other = []
    for drawing in drawings:
        if drawing["items"][0][0] == "c":
            circles.append(drawing)
        elif drawing["items"][0][0] == "re":
            rectangles.append(drawing)
        else:
            other.append(drawing)
    return rectangles, circles, other


def deduplicate(items):
    seen = []
    new = []
    for item in items:
        if not item["rect"] in seen:
            seen.append(item["rect"])
            new.append(item)
    return new


def translation(a, b):
    return (b[0] - a[0], b[1] - a[1])


def better_toc(doc):
    try:
        return doc.toc
    except:
        pass
    toc = {name: [] for _, name in pagenames.items()}
    for page in doc:
        _, _, form = get_spans(page)
        for span in form:
            if "Bold" in span["font"] and span["text"][0] != " ":
                pagetitle = span["text"]
                break
        toc[pagenames[pagetitle]].append(page.number)
    doc.toc = toc
    return doc.toc
