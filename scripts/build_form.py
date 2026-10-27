"""Step 3: build the Chapter Readiness Assessment form from form_spec.json.

Run scripts/verify_properties.py first; option lists come from its output
(scripts/out/properties.json), never from retyped values. Chapter dropdown
options come from the current FAME Chapter records.

The v3 API has no multi-step pages, so each step starts with a rich text
heading group; Jess splits pages in the editor.
"""
import html
import json
import os
import sys

from hubspot import CONTACT, FAME_CHAPTER, call, form_body

HERE = os.path.dirname(os.path.abspath(__file__))
spec = json.load(open(os.path.join(HERE, "..", "form_spec.json")))
props = json.load(open(os.path.join(HERE, "out", "properties.json")))["properties"]


def paragraphs(text):
    """Plain spec text to HTML: blank lines split paragraphs, '- ' lines become a list."""
    out = []
    for block in text.split("\n\n"):
        lines = block.split("\n")
        items = [l[2:] for l in lines if l.startswith("- ")]
        rest = [l for l in lines if not l.startswith("- ")]
        out += [f"<p>{html.escape(l)}</p>" for l in rest]
        if items:
            out.append("<ul>" + "".join(f"<li>{html.escape(i)}</li>" for i in items) + "</ul>")
    return "".join(out)


def rich_group(rich_text):
    return {"groupType": "default_group", "richTextType": "text",
            "richText": rich_text, "fields": []}


def chapter_options():
    status, d = call("GET", f"/crm/v3/objects/{FAME_CHAPTER}?limit=100&properties=fame_chapter_name")
    if status != 200 or d.get("paging"):
        sys.exit(f"Chapter lookup failed or needs paging: {status}")
    names = sorted(r["properties"]["fame_chapter_name"] for r in d["results"])
    return [{"label": n, "value": n, "displayOrder": i} for i, n in enumerate(names)]


def build_field(f):
    obj = FAME_CHAPTER if f["object"] == "fame_chapter" else CONTACT
    out = {"objectTypeId": obj, "name": f["property"], "fieldType": f["fieldType"],
           "label": f["label"], "required": f["required"], "hidden": False,
           "dependentFields": []}
    if f.get("helpText"):
        out["description"] = f["helpText"]
    if f["fieldType"] == "email":
        out["validation"] = {"blockedEmailDomains": [], "useDefaultBlockList": False}
    if f["fieldType"] in ("radio", "multiple_checkboxes", "dropdown"):
        if f["property"] == "fame_chapter_name":
            opts = chapter_options()
        else:
            opts = [{**o, "displayOrder": i} for i, o in enumerate(props[f["property"]]["options"])]
        if not opts:
            sys.exit(f"No options for {f['property']}")
        out["options"] = opts
        out["defaultValues"] = []
    return out


groups = [rich_group(f"<h1>{html.escape(spec['formName'])}</h1>" + paragraphs(spec["introduction"]))]
for step in spec["steps"]:
    heading = f"<h2>{html.escape(step['title'])}</h2>"
    if step.get("intro"):
        heading += paragraphs(step["intro"])
    if step.get("showRatingScale"):
        heading += "<p><strong>How to answer the readiness questions</strong></p>" + "".join(
            f"<p>{html.escape(l)}</p>" for l in spec["ratingScaleHelpText"].split("\n"))
    groups.append(rich_group(heading))
    groups += [{"groupType": "default_group", "richTextType": "text", "richText": "",
                "fields": [build_field(f)]} for f in step["fields"]]

body = form_body(spec["formName"], groups, paragraphs(spec["thankYouMessage"]))

if "--dry-run" in sys.argv:
    print(json.dumps(body, indent=1)[:3000])
    print("fields:", sum(len(g["fields"]) for g in groups), "groups:", len(groups))
    sys.exit()

status, created = call("POST", "/marketing/v3/forms/", body)
print("POST", status)
if status not in (200, 201):
    print(json.dumps(created, indent=1))
    sys.exit(1)
print("form id", created["id"])
json.dump(created, open(os.path.join(HERE, "out", "form_created.json"), "w"), indent=1)
