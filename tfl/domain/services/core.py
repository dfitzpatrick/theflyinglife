import markdown


def open_markdown(fn) -> str:
    with open(fn, "r", encoding="utf-8") as md:
        text = md.read()
    html = markdown.markdown(text)
    return html

