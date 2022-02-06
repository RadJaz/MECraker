import fitz
from .page_mods import *


def fields(in_file, out_file):
    in_file = fitz.open(in_file)
    outdoc = fitz.open()  # create empty PDF
    for in_page in in_file:
        in_page.data
        page = outdoc.new_page(width=612.0, height=792.0)  # create an empty page
        rectshape = page.new_shape()  # start a Shape (canvas)
        textshape = page.new_shape()
        for label, rect in templates[in_page.type].items():
            rectshape.draw_rect(rect["box"])
            textshape.insert_text(get_center(rect["box"]), str(label))
        textshape.insert_text((0, 11), in_page.type)
        rectshape.finish(color=(1, 0, 0), fill=None)
        rectshape.commit()
        textshape.finish(color=(0, 0, 0), fill=(0, 0, 0))
        textshape.commit()
    outdoc.save(out_file)


def seqno(in_file, out_file):
    ref = fitz.open(in_file)
    outdoc = fitz.open()
    for in_page in ref:
        page = outdoc.new_page(width=612.0, height=792.0)
        rectshape = page.new_shape()
        textshape = page.new_shape()
        rectangles, _, _ = sort_drawings(in_page.get_drawings())
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
        textshape.insert_text((0, 11), in_page.type)
        rectshape.finish(color=(0, 0, 0), fill=None)
        rectshape.commit()
        textshape.finish(color=(1, 0, 0), fill=(0, 0, 0))
        textshape.commit()
    outdoc.save(out_file)
