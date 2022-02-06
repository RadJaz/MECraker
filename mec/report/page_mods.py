import fitz
import json
import os
from .utils import *

fitz.Page.get_spans = get_spans

templates = {}


def _load_template(page):
    templatepath = os.path.join("templates", page.type + ".json")
    with open(templatepath) as f:
        templates[page.type] = json.load(f)
    rectangles, _, _ = sort_drawings(page.get_drawings())
    for box in templates[page.type]:
        if type(templates[page.type][box]["box"]) == int:
            for rect in rectangles:
                if rect["seqno"] == templates[page.type][box]["box"]:
                    templates[page.type][box]["box"] = rect["rect"]
        else:
            for i in range(len(templates[page.type][box]["box"])):
                for rect in rectangles:
                    if templates[page.type][box]["box"][i] == -1:
                        templates[page.type][box]["box"][i] = page.bound()[i]
                    elif rect["seqno"] == templates[page.type][box]["box"][i]:
                        if i == 0:
                            templates[page.type][box]["box"][i] = rect["rect"].x1
                        elif i == 1:
                            templates[page.type][box]["box"][i] = rect["rect"].y1
                        elif i == 2:
                            templates[page.type][box]["box"][i] = rect["rect"].x0
                        elif i == 3:
                            templates[page.type][box]["box"][i] = rect["rect"].y0
            templates[page.type][box]["box"] = fitz.Rect(
                templates[page.type][box]["box"]
            )


def _page__getattr__(page, attr):
    if attr == "data":
        if page.type not in templates:
            _load_template(page)
        template = templates[page.type]
        checkmarks, input, _ = page.get_spans()
        data = {label: "" for label, _ in template.items()}
        for label, dict in template.items():
            rect = dict["box"]
            if dict["type"] == "bool":
                data[label] = False
                for span in checkmarks:
                    if rect.contains(get_center(span["bbox"])):
                        data[label] = True
            else:
                for span in input:
                    if rect.contains(get_center(span["bbox"])):
                        if data[label]:
                            data[label] += "\n"
                        data[label] += span["text"]
                if dict["type"] == "str":
                    pass
                elif dict["type"] == "float":
                    data[label] = float(data[label])
                elif dict["type"] == "int":
                    data[label] = int(data[label])
                elif dict["type"] == "date":
                    data[label] = datetime.strptie(data[label], dict["format"])
        page.data = data
        return page.data
    elif attr == "type":
        _, _, form = get_spans(page)
        for span in form:
            if "Bold" in span["font"] and span["text"][0] != " ":
                pagetitle = span["text"]
                page.type = pagenames[pagetitle]
                return page.type
    raise AttributeError


fitz.Page.__getattr__ = _page__getattr__


def _page__getitem__(page, item):
    return page.data[item]


fitz.Page.__getitem__ = _page__getitem__
