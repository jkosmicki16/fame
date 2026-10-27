# Build log

## Step 0: chapter matching (2026-10-27): done
- Jess chose a **required dropdown** of `fame_chapter_name` as the first field on the Chapter Information page.
- Jess confirmed **one page per section**, matching `docs/Chapter_Readiness_Assessment_Details.pdf`.
- Recorded both in `form_spec.json` (`chapterMatching`, `layout`, and the first Chapter Information field).
- I didn't look up the 3 existing forms that use `fame_chapter_name`: `HUBSPOT_ACCESS_TOKEN` isn't set in this session, and Jess decided without comparing them.

## Step 1: verify properties (2026-10-27): done, with issues for Jess
- Auth: the network secret is added to api.hubapi.com requests by the proxy. No token is read in the session. The `HUBSPOT_ACCESS_TOKEN` env var isn't used.
- FAME Chapter objectTypeId: `2-41718997`. There are 57 chapter records, all named, with no duplicate names.
- Ran `scripts/verify_properties.py`. All 99 FAME Chapter properties exist. Every `multi_line_text` field is `textarea`.
- Option sets match the PDF. The rating scale has 4 options: Fully in Place | Partially in Place | Needs Development | Unsure / Needs Discussion.
- 53 radio questions are stored as `select` properties. This is harmless: they're all enumerations, and the form sets its own radio display. No change.
- **Issue:** `fame_chapter_name` is a text property, not a dropdown, so it has no options. Waiting on Jess.
- **Issue:** the 3 contact properties returned 403 because the private app lacks `crm.objects.contacts.read`. firstname, lastname and email are standard properties, so this is not blocking.
