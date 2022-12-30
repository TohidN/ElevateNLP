from django import template

register = template.Library()


@register.filter(is_safe=True)
def visualize_displacy_ent(analysis):
    from spacy import displacy

    content = {}
    content["text"] = analysis.phrase.text
    content["ents"] = []
    content["title"] = None
    if "ner" in analysis.data and len(analysis.data["ner"]) > 0:
        for i, item in analysis.data["ner"].items():
            content["ents"].append(
                {
                    "start": item["start_char"],
                    "end": item["end_char"],
                    "label": item["type"],
                }
            )
    html = displacy.render(content, style="ent", manual=True)
    return html


@register.filter(is_safe=True)
def visualize_displacy_dep(analysis):
    from spacy import displacy

    content = {}
    content["words"] = []
    content["arcs"] = []
    try:
        if len(analysis.data["words"]) > 0:
            for i, item in analysis.data["words"].items():
                content["words"].append({"text": item["text"], "tag": item["upos"]})
                if item["dep_rel"].lower() != "root":
                    if item["id"] > item["dep_parent"]:
                        content["arcs"].append(
                            {
                                "start": int(item["dep_parent"]),
                                "end": int(item["id"]),
                                "label": item["dep_rel"],
                                "dir": "right",
                            }
                        )
                    elif item["id"] < item["dep_parent"]:
                        content["arcs"].append(
                            {
                                "start": int(item["id"]),
                                "end": int(item["dep_parent"]),
                                "label": item["dep_rel"],
                                "dir": "left",
                            }
                        )
        options = {
            "bg": "Transparent",
        }
        html = displacy.render(content, style="dep", manual=True, options=options)
        return html
    except Exception:
        return ""
