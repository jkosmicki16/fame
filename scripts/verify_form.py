"""Step 4: GET the built form and check it against form_spec.json."""
import html
import json
import os
import sys

from hubspot import call

HERE = os.path.dirname(os.path.abspath(__file__))
spec = json.load(open(os.path.join(HERE, "..", "form_spec.json")))
props = json.load(open(os.path.join(HERE, "out", "properties.json")))["properties"]
form_id = sys.argv[1]

status, form = call("GET", f"/marketing/v3/forms/{form_id}")
if status != 200:
    sys.exit(f"GET failed: {status} {form}")

# Split saved groups into steps at each <h2> heading group.
steps, current = [], None
for g in form["fieldGroups"]:
    if not g.get("fields") and "<h2>" in (g.get("richText") or ""):
        current = []
        steps.append(current)
    elif current is not None:
        current += g.get("fields", [])

problems = []
total = sum(len(s) for s in steps)
print(f"{form['name']} | id {form['id']} | archived {form['archived']}")
print(f"Total fields: {total} (expected {spec['expectedFieldCount']})")
for step, saved in zip(spec["steps"], steps):
    print(f"  {step['title']}: {len(saved)} (expected {len(step['fields'])})")
    for want, got in zip(step["fields"], saved):
        checks = {
            "name": (want["property"], got["name"]),
            "label": (want["label"], html.unescape(got["label"])),
            "required": (want["required"], got["required"]),
            "fieldType": (want["fieldType"], got["fieldType"]),
            "helpText": (want.get("helpText", ""), got.get("description", "")),
        }
        if want["property"] in props and props[want["property"]]["options"]:
            checks["options"] = ([o["value"] for o in props[want["property"]]["options"]],
                                 [o["value"] for o in got.get("options", [])])
        for k, (a, b) in checks.items():
            if a != b:
                problems.append(f"{step['title']} / {want['property']}: {k} spec={a!r} saved={b!r}")
if len(steps) != len(spec["steps"]) or total != spec["expectedFieldCount"]:
    problems.append("step or field count mismatch")
ty = form["configuration"]["postSubmitAction"]
print("Thank-you:", ty["type"], "|", len(ty["value"]), "chars")
chapter = next(f for s in steps for f in s if f["name"] == "fame_chapter_name")
print("Chapter dropdown options:", len(chapter["options"]))
print("Problems:", len(problems))
for p in problems:
    print("  ", p)
