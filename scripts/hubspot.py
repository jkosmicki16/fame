"""Minimal HubSpot API client.

Auth: the session's network secret is added to api.hubapi.com requests by the
egress proxy, so no token is read or handled here.
"""
import json
import urllib.error
import urllib.request

BASE = "https://api.hubapi.com"
FAME_CHAPTER = "2-41718997"
CONTACT = "0-1"


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            return r.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except ValueError:
            return e.code, raw.decode(errors="replace")


# Settings copied from the existing "Alabama State Training Registration" form,
# minus its notification recipients.
CONFIGURATION = {
    "language": "en",
    "cloneable": True,
    "editable": True,
    "archivable": True,
    "recaptchaEnabled": False,
    "notifyContactOwner": False,
    "notifyRecipients": [],
    "createNewContactForNewEmail": False,
    "prePopulateKnownValues": True,
    "allowLinkToResetKnownValues": False,
    "lifecycleStages": [],
}
DISPLAY_OPTIONS = {
    "renderRawHtml": False,
    "theme": "default_style",
    "submitButtonText": "Submit",
    "style": {
        "fontFamily": "helvetica",
        "backgroundWidth": "100%",
        "labelTextColor": "#0032A0",
        "labelTextSize": "13px",
        "helpTextColor": "#516383DE",
        "helpTextSize": "11px",
        "legalConsentTextColor": "#33475B",
        "legalConsentTextSize": "14px",
        "submitColor": "#2CCCD3",
        "submitAlignment": "left",
        "submitFontColor": "#ffffff",
        "submitSize": "12px",
    },
    "cssClass": "hs-form stacked",
}


def form_body(name, field_groups, thank_you_html):
    return {
        "formType": "hubspot",
        "name": name,
        "archived": False,
        "createdAt": "2026-10-27T00:00:00Z",
        "updatedAt": "2026-10-27T00:00:00Z",
        "configuration": {**CONFIGURATION,
                          "postSubmitAction": {"type": "thank_you", "value": thank_you_html}},
        "displayOptions": DISPLAY_OPTIONS,
        "legalConsentOptions": {"type": "none"},
        "fieldGroups": field_groups,
    }
