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
- Jess chose a **form-only dropdown** for `fame_chapter_name`, built from the 57 chapter names in HubSpot. The property stays text.
- Step 0 comparison: only 1 active form uses `fame_chapter_name` ("Alabama State Training Registration Form - 6/2-6/5"), not 3. It uses a required single-line text field. None of the 6 archived forms use it.

## Step 2: feasibility test (2026-10-27): done
- Read the current Forms v3 reference (`/docs/api-reference/legacy/marketing/forms/create-form.md`). HubSpot now labels v3 "legacy".
- `scripts/feasibility_test.py` created "TEST - Readiness Assessment" (id 88ee65cb-…) with email (0-1), readiness_assessment_date (FAME Chapter) and a 2-option dropdown on fame_chapter_name. POST returned 201, and the GET showed all 3 fields saved with the right object and type.
- The script crashed on an output path before its delete. I deleted the form by hand (DELETE 204, then GET 404) and fixed the path.
- **No multi-step support** in the v3 schema: field groups only, with no pages or steps. Plan: a single page with a rich-text heading per step. Jess splits the pages in the editor.
- **No draft state** in the v3 schema or response: there's no published or draft field. Waiting on Jess before step 3.
- Not tested: whether a submission updates the existing chapter record or creates a new one. Testing that needs a real submission, which writes CRM data.

## Step 3: build (2026-10-27): done
- `scripts/build_form.py` created **Chapter Readiness Assessment**, id `d72951eb-6e96-4bd0-b2b7-437f2b7caa96` (POST 201).
- Layout: an intro rich text block, then a rich text heading for each step (title and intro), then one field per group. The rating scale help text is in the Employer Engagement heading. The thank-you message is inline.
- Options come from `scripts/out/properties.json`. The chapter dropdown has 57 options, sorted, taken from the current FAME Chapter records.
- Not shared or embedded anywhere. Jess will check its draft or live status in the editor.

## Step 4: verify (2026-10-27): done
- `scripts/verify_form.py` read the form back: 102 fields, and every step count matches. Every name, label, required flag, field type, help text and option list matches the spec.
- HubSpot stores labels as HTML (`&` saved as `&amp;`), the same as other forms in the portal. It still shows as "&".
- Editor: https://app.hubspot.com/forms/21436812/editor/d72951eb-6e96-4bd0-b2b7-437f2b7caa96/edit/form

## For Jess to do in the editor
- Split the 10 headed sections into pages (the API can't make multi-step forms).
- Check the form's draft or live status.
- Make one test submission to confirm it updates the chosen chapter's existing record rather than creating a new one.
- If a new chapter is added in HubSpot, add it to the Chapter Name dropdown on the form.
- Possibly add the `crm.objects.contacts.read` scope to the private app. Not needed for this build.
