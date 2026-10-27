"""Step 1: look up the FAME Chapter objectTypeId and check every spec property.

Auth: the session's network secret is added to api.hubapi.com requests by the
egress proxy, so no token is read or handled here. Read-only.
Writes scripts/out/properties.json.
"""
import json
import os
import sys
import urllib.error
import urllib.request

BASE = "https://api.hubapi.com"
HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "..", "form_spec.json")
OUT = os.path.join(HERE, "out", "properties.json")

# Spec fieldType -> HubSpot property fieldType
EXPECTED = {
    "radio": "radio",
    "multiple_checkboxes": "checkbox",
    "dropdown": "select",
    "single_line_text": "text",
    "multi_line_text": "textarea",
    "number": "number",
    "datepicker": "date",
    "email": "text",
}


def get(path):
    try:
        with urllib.request.urlopen(BASE + path) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def main():
    spec = json.load(open(SPEC))
    fqn = spec["chapterObject"]["fullyQualifiedName"]

    status, schemas = get("/crm/v3/schemas")
    if status != 200:
        sys.exit(f"GET /crm/v3/schemas failed: {status} {schemas}")
    match = [s for s in schemas["results"] if s["fullyQualifiedName"] == fqn]
    if not match:
        sys.exit(f"No schema with fullyQualifiedName {fqn}")
    object_type_id = match[0]["objectTypeId"]
    print(f"FAME Chapter objectTypeId: {object_type_id}")

    fields = [f for step in spec["steps"] for f in step["fields"]]
    results, missing, mismatched = {}, [], []
    for f in fields:
        obj = object_type_id if f["object"] == "fame_chapter" else "0-1"
        status, prop = get(f"/crm/v3/properties/{obj}/{f['property']}")
        if status != 200:
            missing.append((f["object"], f["property"], status, prop.get("message")))
            continue
        results[f["property"]] = {
            "objectTypeId": obj,
            "label": prop.get("label"),
            "type": prop.get("type"),
            "fieldType": prop.get("fieldType"),
            "options": [
                {"label": o["label"], "value": o["value"]}
                for o in sorted(prop.get("options", []), key=lambda o: o.get("displayOrder", 0))
                if not o.get("hidden")
            ],
        }
        want = EXPECTED[f["fieldType"]]
        if prop.get("fieldType") != want:
            mismatched.append((f["property"], f["fieldType"], want, prop.get("fieldType"), prop.get("type")))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"objectTypeId": object_type_id, "properties": results}, open(OUT, "w"), indent=2)

    print(f"Checked {len(fields)} fields: {len(results)} found, {len(missing)} missing, {len(mismatched)} type mismatches")
    for m in missing:
        print("MISSING", *m)
    for m in mismatched:
        print("MISMATCH {} spec={} expected={} actual={} (type {})".format(*m))


if __name__ == "__main__":
    main()
