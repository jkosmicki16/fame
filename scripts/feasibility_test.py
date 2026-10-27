"""Step 2: create a small test form, GET it back, then delete it.

Checks that the Forms API accepts FAME Chapter fields, including a form-only
dropdown on the text property fame_chapter_name.
"""
import json
import os
import sys

from hubspot import CONTACT, FAME_CHAPTER, call, form_body


def group(fields, rich_text=""):
    return {"groupType": "default_group", "richTextType": "text",
            "richText": rich_text, "fields": fields}


def field(obj, name, field_type, label, required, **extra):
    return {"objectTypeId": obj, "name": name, "fieldType": field_type, "label": label,
            "required": required, "hidden": False, "dependentFields": [], **extra}


fields = [
    field(CONTACT, "email", "email", "Email", True,
          validation={"blockedEmailDomains": [], "useDefaultBlockList": False}),
    field(FAME_CHAPTER, "readiness_assessment_date", "datepicker", "Assessment date", True),
    field(FAME_CHAPTER, "fame_chapter_name", "dropdown", "Chapter Name", True,
          defaultValues=[],
          options=[{"label": "Test Chapter A", "value": "Test Chapter A", "displayOrder": 0},
                   {"label": "Test Chapter B", "value": "Test Chapter B", "displayOrder": 1}]),
]
body = form_body("TEST - Readiness Assessment",
                 [group([f]) for f in fields],
                 "<p>Test</p>")

status, created = call("POST", "/marketing/v3/forms/", body)
print("POST", status)
if status not in (200, 201):
    print(json.dumps(created, indent=1))
    sys.exit(1)
form_id = created["id"]
print("form id", form_id)

status, got = call("GET", f"/marketing/v3/forms/{form_id}")
print("GET", status)
saved = {f["name"]: f for g in got["fieldGroups"] for f in g.get("fields", [])}
for f in fields:
    s = saved.get(f["name"])
    print(" ", f["name"], "->",
          "MISSING" if not s else f"{s['objectTypeId']} {s['fieldType']} required={s['required']} options={len(s.get('options', []))}")
print("top-level keys:", sorted(got.keys()))
json.dump(got, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "test_form.json"), "w"), indent=1)

if "--keep" not in sys.argv:
    status, _ = call("DELETE", f"/marketing/v3/forms/{form_id}")
    print("DELETE", status)
