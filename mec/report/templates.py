import fitz
from .utils import *


def convert_templates(templates, reference="reference.pdf"):
    with open(reference, "rb") as ref:
        ref = ref.read()
    ref = fitz.open(stream=ref, filetype="pdf")
    toc = better_toc(ref)
    for t in templates:
        page = ref[toc[t][0]]
        rectangles, _, _ = sort_drawings(page.get_drawings())
        for box in templates[t]:
            for i in range(len(templates[t][box])):
                for rect in rectangles:
                    if templates[t][box][i] == -1:
                        templates[t][box][i] = page.bound()[i]
                        continue
                    if rect["seqno"] == templates[t][box][i]:
                        if i == 0:
                            templates[t][box][i] = rect["rect"].x1
                        elif i == 1:
                            templates[t][box][i] = rect["rect"].y1
                        elif i == 2:
                            templates[t][box][i] = rect["rect"].x0
                        elif i == 3:
                            templates[t][box][i] = rect["rect"].y0
                        continue
            templates[t][box] = fitz.Rect(templates[t][box])
    return templates


def convert_checkbox_templates(checkbox_templates, reference="reference.pdf"):
    with open(reference, "rb") as ref:
        ref = ref.read()
    ref = fitz.open(stream=ref, filetype="pdf")
    toc = better_toc(ref)
    for t in checkbox_templates:
        page = ref[toc[t][0]]
        rectangles, _, _ = sort_drawings(page.get_drawings())
        for checkbox in checkbox_templates[t]:
            for rect in rectangles:
                if rect["seqno"] == checkbox_templates[t][checkbox]:
                    checkbox_templates[t][checkbox] = rect["rect"]
    return checkbox_templates


def generate_visual(templates, filename="visual.pdf"):
    outdoc = fitz.open()  # create empty PDF
    for t in templates:
        page = outdoc.new_page(width=612.0, height=792.0)  # create an empty page
        rectshape = page.new_shape()  # start a Shape (canvas)
        textshape = page.new_shape()
        for label, rect in templates[t].items():
            rectshape.draw_rect(rect)
            textshape.insert_text(get_center(rect), str(label))
        textshape.insert_text((0, 11), t)
        rectshape.finish(color=(1, 0, 0), fill=None)
        rectshape.commit()
        textshape.finish(color=(0, 0, 0), fill=(0, 0, 0))
        textshape.commit()
    outdoc.save(filename)


def generate_seqno_visual(reference, filename="seqno_visual.pdf"):
    with open(reference, "rb") as ref:
        ref = ref.read()
    ref = fitz.open(stream=ref, filetype="pdf")
    toc = better_toc(ref)
    outdoc = fitz.open()
    for t in templates:
        page = outdoc.new_page(width=612.0, height=792.0)
        rectshape = page.new_shape()
        textshape = page.new_shape()
        rectangles, _, _ = sort_drawings(ref[toc[t][0]].get_drawings())
        for rect in rectangles:
            ratio = rect["rect"].width / rect["rect"].height
            if 0.1 < ratio < 10:
                continue
            if ratio < 1:
                rotate = 90
            else:
                rotate = 0
            rectshape.draw_rect(rect["rect"])
            textshape.insert_text(
                get_center(rect["rect"]),
                str(rect["seqno"]),
                color=(1, 0, 0),
                rotate=rotate,
            )
        checkboxes = []
        for rect in rectangles:
            ratio = rect["rect"].width / rect["rect"].height
            if ratio < 3 / 4 or ratio > 4 / 3:
                continue
            if rect["fill"] == (1, 1, 1):
                continue
            checkboxes.append(rect)
        checkboxes = deduplicate(checkboxes)
        for rect in checkboxes:
            rectshape.draw_rect(rect["rect"])
            textshape.insert_textbox(
                rect["rect"], str(rect["seqno"]), color=(1, 0, 0), fontsize=6, align=1
            )
        textshape.insert_text((0, 11), t)
        rectshape.finish(color=(0, 0, 0), fill=None)
        rectshape.commit()
        textshape.finish(color=(1, 0, 0), fill=(0, 0, 0))
        textshape.commit()
    outdoc.save(filename)


templates = {
    "100+": {
        "1a": [4, 10, 6, 11],
        "1b": [6, 10, 5, 11],
        "1c": [5, 10, 2, 11],
        "1d": [2, 10, 3, 11],
        "2a": [4, 11, 6, 12],
        "2b": [6, 11, 5, 12],
        "2c": [5, 11, 2, 12],
        "2d": [2, 11, 3, 12],
        "3a": [4, 12, 6, 13],
        "3b": [6, 12, 5, 13],
        "3c": [5, 12, 2, 13],
        "3d": [2, 12, 3, 13],
        "4a": [4, 13, 6, 14],
        "4b": [6, 13, 5, 14],
        "4c": [5, 13, 2, 14],
        "4d": [2, 13, 3, 14],
        "5a": [4, 14, 6, 15],
        "5b": [6, 14, 5, 15],
        "5c": [5, 14, 2, 15],
        "5d": [2, 14, 3, 15],
        "6a": [4, 15, 6, 16],
        "6b": [6, 15, 5, 16],
        "6c": [5, 15, 2, 16],
        "6d": [2, 15, 3, 16],
        "7a": [4, 16, 6, 17],
        "7b": [6, 16, 5, 17],
        "8c": [5, 16, 2, 17],
        "8d": [2, 16, 3, 17],
        "9a": [4, 17, 6, 18],
        "9b": [6, 17, 5, 18],
        "9c": [5, 17, 2, 18],
        "9d": [2, 17, 3, 18],
        "10a": [4, 18, 6, 19],
        "10b": [6, 18, 5, 19],
        "10c": [5, 18, 2, 19],
        "10d": [2, 18, 3, 19],
        "11a": [4, 19, 6, 20],
        "11b": [6, 19, 5, 20],
        "11c": [5, 19, 2, 20],
        "11d": [2, 19, 3, 20],
        "12a": [4, 20, 6, 21],
        "12b": [6, 20, 5, 21],
        "12c": [5, 20, 2, 21],
        "12d": [2, 20, 3, 21],
        "13a": [4, 21, 6, 22],
        "13b": [6, 21, 5, 22],
        "13c": [5, 21, 2, 22],
        "13d": [2, 21, 3, 22],
        "14a": [4, 22, 6, 23],
        "14b": [6, 22, 5, 23],
        "14c": [5, 22, 2, 23],
        "14d": [2, 22, 3, 23],
        "15a": [4, 23, 6, 24],
        "15b": [6, 23, 5, 24],
        "15c": [5, 23, 2, 24],
        "15d": [2, 23, 3, 24],
        "16a": [4, 24, 6, 25],
        "16b": [6, 24, 5, 25],
        "16c": [5, 24, 2, 25],
        "16d": [2, 24, 3, 25],
        "data": [5, 8, 3, 9],
        "name": [4, 8, 5, 9],
        "total": [2, 25, 3, 26],
    },
    "<100": {
        "10a": [6, 20, 4, 21],
        "10b": [4, 20, 5, 21],
        "11a": [6, 21, 4, 22],
        "11b": [4, 21, 5, 22],
        "12a": [6, 22, 4, 23],
        "12b": [4, 22, 5, 23],
        "13a": [6, 23, 4, 24],
        "13b": [4, 23, 5, 24],
        "14a": [6, 24, 4, 25],
        "14b": [4, 24, 5, 25],
        "15a": [6, 25, 4, 26],
        "15b": [4, 25, 5, 26],
        "16a": [6, 26, 4, 27],
        "16b": [4, 26, 5, 27],
        "17a": [6, 27, 4, 28],
        "17b": [4, 27, 5, 28],
        "18a": [6, 28, 4, 29],
        "18b": [4, 28, 5, 29],
        "19a": [6, 29, 4, 30],
        "19b": [4, 29, 5, 30],
        "1a": [6, 11, 4, 12],
        "1b": [4, 11, 5, 12],
        "20a": [6, 30, 4, 31],
        "20b": [4, 30, 5, 31],
        "21a": [6, 31, 4, 32],
        "21b": [4, 31, 5, 32],
        "22a": [6, 32, 4, 33],
        "22b": [4, 32, 5, 33],
        "2a": [6, 12, 4, 13],
        "2b": [4, 12, 5, 13],
        "3a": [6, 13, 4, 14],
        "3b": [4, 13, 5, 14],
        "4a": [6, 14, 4, 15],
        "4b": [4, 14, 5, 15],
        "5a": [6, 15, 4, 16],
        "5b": [4, 15, 5, 16],
        "6a": [6, 16, 4, 17],
        "6b": [4, 16, 5, 17],
        "7a": [6, 17, 4, 18],
        "7b": [4, 17, 5, 18],
        "8a": [6, 18, 4, 19],
        "8b": [4, 18, 5, 19],
        "9a": [6, 19, 4, 20],
        "9b": [4, 19, 5, 20],
        "date": [7, 9, 5, 10],
        "name": [6, 9, 7, 10],
        "total": [4, 33, 5, 34],
    },
    "c/l": {
        "1": [5, 0, 2, 9],
        "2": [2, 0, 4, 9],
        "6": [3, 46, 4, 47],
        "7": [3, 47, 4, 48],
        "8": [3, 48, 4, 49],
        "9": [3, 49, 4, 50],
        "10": [3, 50, 4, 51],
        "11": [3, 52, 4, 53],
        "12": [3, 53, 4, 54],
        "13": [3, 54, 4, 55],
        "14": [3, 55, 4, 56],
        "18": [3, 56, 4, 60],
        "19": [3, 60, 4, 61],
        "20": [3, 61, 4, 62],
        "21": [3, 62, 4, 63],
        "22": [3, 63, 4, 64],
        "23": [3, 64, 4, 65],
        "15a": [5, 57, 3, 58],
        "15b": [5, 58, 3, 59],
        "16a": [6, 57, 3, 58],
        "16b": [6, 58, 3, 59],
        "17a": [3, 57, 4, 58],
        "17b": [3, 58, 4, 59],
        "3a": [5, 31, 2, 34],
        "3b": [5, 34, 2, 37],
        "3c": [5, 37, 2, 40],
        "3d": [5, 40, 2, 43],
        "3e": [5, 43, 2, 46],
        "4a": [2, 31, 3, 34],
        "4b": [2, 34, 3, 37],
        "4c": [2, 37, 3, 40],
        "4d": [2, 40, 3, 43],
        "4e": [2, 43, 3, 46],
        "5a": [3, 31, 4, 34],
        "5b": [3, 34, 4, 37],
        "5c": [3, 37, 4, 40],
        "5d": [3, 40, 4, 43],
        "5e": [3, 43, 4, 46],
    },
    "contributions": {
        "3a": [9, 38, 11, 41],
        "3b": [9, 41, 11, 44],
        "3c": [9, 44, 11, 47],
        "3d": [9, 47, 11, 50],
        "3e": [9, 50, 11, 53],
        "3f": [9, 53, 11, 56],
        "3g": [9, 56, 11, 59],
        "3h": [9, 59, 11, 62],
        "4a": [11, 38, 7, 41],
        "4b": [11, 41, 7, 44],
        "4c": [11, 44, 7, 47],
        "4d": [11, 47, 7, 50],
        "4e": [11, 50, 7, 53],
        "4f": [11, 53, 7, 56],
        "4g": [11, 56, 7, 59],
        "4h": [11, 59, 7, 62],
        "5a": [7, 38, 8, 41],
        "5b": [7, 41, 8, 44],
        "5c": [7, 44, 8, 47],
        "5d": [7, 47, 8, 50],
        "5e": [7, 50, 8, 53],
        "5f": [7, 53, 8, 56],
        "5g": [7, 56, 8, 59],
        "5h": [7, 59, 8, 62],
        "date": [10, 13, 3, 14],
        "name": [2, 13, 10, 14],
        "total": [9, 62, 8, 63],
    },
    "cover": {
        "MECID": [-1, -1, 6, 14],
        "1": [6, 13, 7, 14],
        "2": [9, 14, 8, 15],
        "3": [9, 15, 3, 17],
        "4": [3, 15, 8, 17],
        "5": [9, 17, 8, 18],
        "6": [9, 18, 4, 20],
        "7": [4, 18, 8, 20],
        "8": [9, 20, 8, 21],
        "9": [9, 21, 10, 23],
        "10": [10, 21, 8, 23],
        "11": [9, 23, 11, 24],
        "12": [11, 23, 8, 24],
        "13": [9, 24, 8, 25],
        "14": [9, 25, 12, 27],
        "15": [12, 25, 8, 27],
        "16": [9, 27, 12, 29],
        "17": [12, 27, 8, 29],
    },
    "e/c": {
        "1": [5, 9, 2, 10],
        "2": [2, 9, 4, 10],
        "5": [3, 13, 4, 14],
        "6": [3, 14, 4, 15],
        "7": [3, 15, 4, 16],
        "12": [35, 20, 38, 21],
        "13": [35, 21, 38, 41],
        "14": [35, 41, 38, 42],
        "15": [35, 42, 38, 43],
        "16": [35, 43, 38, 44],
        "17": [35, 44, 38, 45],
        "18": [35, 45, 38, 46],
        "19": [35, 46, 38, 47],
        "23": [35, 51, 38, 52],
        "24": [35, 52, 38, 53],
        "26": [35, 56, 38, 57],
        "27": [35, 57, 38, 58],
        "28": [35, 58, 38, 59],
        "10a": [6, 17, 3, 18],
        "10b": [6, 18, 3, 19],
        "10c": [6, 19, 3, 20],
        "11a": [3, 17, 4, 18],
        "11b": [3, 18, 4, 19],
        "11c": [3, 19, 4, 20],
        "20a": [36, 48, 34, 49],
        "20b": [36, 49, 34, 50],
        "20c": [36, 50, 34, 51],
        "21a": [34, 48, 35, 49],
        "21b": [34, 49, 35, 50],
        "21c": [34, 50, 35, 51],
        "22a": [35, 48, 38, 49],
        "22b": [35, 49, 38, 50],
        "22c": [35, 50, 38, 51],
        "25a": [35, 53, 38, 54],
        "25b": [35, 54, 38, 55],
        "3a": [5, 11, 3, 12],
        "3b": [5, 12, 3, 13],
        "4a": [3, 11, 4, 12],
        "4b": [3, 12, 4, 13],
        "8a": [5, 17, 7, 18],
        "8b": [5, 18, 7, 19],
        "8c": [5, 19, 7, 20],
        "9a": [7, 17, 6, 18],
        "9b": [7, 18, 6, 19],
        "9c": [7, 19, 6, 20],
    },
    "summary": {
        "1": [2, 15, 3, 16],
        "2": [1, 16, 2, 17],
        "3": [1, 17, 2, 18],
        "4": [1, 18, 2, 19],
        "5": [1, 19, 2, 20],
        "6": [1, 20, 2, 21],
        "7": [1, 21, 2, 22],
        "8": [2, 22, 3, 23],
        "9": [10, 24, 11, 25],
        "10": [9, 25, 10, 26],
        "11": [29, 26, 30, 27],
        "12": [29, 27, 30, 43],
        "13": [29, 43, 30, 44],
        "14": [30, 44, 31, 45],
        "15": [34, 46, 35, 47],
        "16": [33, 47, 34, 78],
        "17": [33, 49, 34, 50],
        "18": [33, 50, 34, 51],
        "19": [34, 51, 35, 52],
        "20": [37, 53, 38, 54],
        "21": [37, 54, 38, 55],
        "22": [37, 55, 38, 56],
        "23": [37, 56, 38, 57],
        "24": [12, 18, 7, 20],
        "25": [12, 20, 7, 22],
        "26": [12, 22, 7, 24],
        "27": [12, 24, 7, 26],
        "28": [41, 43, 40, 44],
        "29": [41, 44, 40, 46],
        "31": [41, 49, 40, 51],
        "32": [41, 51, 40, 53],
        "33": [41, 53, 40, 55],
        "34": [41, 55, 40, 57],
        "30a": [41, 46, 40, 48],
        "30b": [41, 48, 40, 49],
        "date": [5, 13, 6, 14],
        "name": [4, 13, 5, 14],
    },
    "explanation": {},
    "addendum": {"MECID": [-1, -1, -1, 2], "body": [0, 3, 1, 4]},
}

checkbox_templates = {
    "cover": {
        "CHECK IF INCUMBENT": 193,
        "REPUBLICAN": 197,
        "DEMOCRAT": 201,
        "OTHER PARTY": 205,
        "CHECK IF NO DEPUTY TREASURER": 125,
        "15 DAYS AFTER CAUCUS NOMINATION": 128,
        "COMMITTEE QUARTERLY REPORT": 132,
        "Jan 15": 176,
        "Apr 15": 180,
        "Jul 15": 184,
        "Oct 15": 188,
        "8 DAYS BEFORE": 136,
        "30 DAYS AFTER ELECTION": 140,
        "TERMINATION": 144,
        "SEMIANNUAL DEBT REPORT": 148,
        "JAN 15": 169,
        "JUL 15": 172,
        "ANNUAL SUPPLEMENTAL": 152,
        "15 DAYS AFTER PETITION DEADLINE": 156,
        "OTHER": 160,
        "AMMENDING PREVIOUS REPORT DATED": 164,
    },
    "100+": {
        "1 PAID": 151,
        "1 INCURRED": 155,
        "2 PAID": 159,
        "2 INCURRED": 162,
        "3 PAID": 167,
        "3 INCURRED": 171,
        "4 PAID": 175,
        "4 INCURRED": 179,
        "5 PAID": 183,
        "5 INCURRED": 187,
        "6 PAID": 190,
        "6 INCURRED": 195,
        "7 PAID": 199,
        "7 INCURRED": 203,
        "8 PAID": 207,
        "8 INCURRED": 210,
        "9 PAID": 215,
        "9 INCURRED": 219,
        "10 PAID": 223,
        "10 INCURRED": 227,
        "11 PAID": 231,
        "11 INCURRED": 235,
        "12 PAID": 239,
        "12 INCURRED": 243,
        "13 PAID": 247,
        "13 INCURRED": 250,
        "14 PAID": 255,
        "14 INCURRED": 259,
        "15 PAID": 263,
        "15 INCURRED": 267,
    },
    "<100": {},
    "c/l": {},
    "contributions": {},
    "e/c": {},
    "summary": {},
    "explanation": {},
    "addendum": {},
}

templates = convert_templates(templates)
checkbox_templates = convert_checkbox_templates(checkbox_templates)
# generate_seqno_visual('reference.pdf')
# generate_visual(templates)
