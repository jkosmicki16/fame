# FAME Chapter Readiness Assessment: HubSpot form build

## Goal
Build a **draft** HubSpot form named "Chapter Readiness Assessment" in portal 21436812 (The Manufacturing Institute) using the HubSpot Forms API. Every field and label is defined in `form_spec.json`. Answers write to the FAME Chapter custom object (`p21436812_fame_chapters`); the person submitting is captured with standard contact fields.

## Ground rules
- Never publish the form. Draft only.
- Never create, edit, or delete CRM properties without asking Jess first and getting a yes.
- Read the HubSpot token from the `HUBSPOT_ACCESS_TOKEN` environment variable. Never print it, log it, or write it to a file.
- Put scripts in `scripts/` and write a short run log to `build_log.md` after each step.
- Before writing API calls, check the current Forms API v3 docs (developers.hubspot.com/docs/api/marketing/forms). Don't rely on memory for request shapes.
- If an API call fails, show Jess the error and your proposed fix before trying something different.

## Steps

### 0. Settle chapter matching
`chapterMatching.method` in the spec is `TBD`. Ask Jess which method to use before building: a dropdown of `fame_chapter_name`, a hidden field set by a per-chapter link, or the approach used by the 3 existing forms that already use `fame_chapter_name` (look those forms up with the API so she can compare). Record her answer in the spec.

### 1. Verify properties
- Look up the FAME Chapter `objectTypeId` (format `2-XXXXXXX`) with `GET /crm/v3/schemas`.
- Fetch every FAME Chapter property in the spec with `GET /crm/v3/properties/{objectType}/{name}`. Confirm each exists and save its `fieldType` and `options`.
- Report any property whose `fieldType` doesn't match the spec. In particular, every `multi_line_text` field should be `textarea`. Ask before changing anything.

### 2. Feasibility test
Create a small test draft form called "TEST - Readiness Assessment" with only `email` (contact, `0-1`) and `readiness_assessment_date` (FAME Chapter). Confirm with a GET that the FAME Chapter field saved. Then delete the test form.
- If the API won't accept FAME Chapter fields, stop. Tell Jess, and lay out the options: build the form in the HubSpot editor, or mirror the fields on Contact and copy them to the chapter with a workflow.
- Also check whether the API supports multi-step forms. If it doesn't, plan a single-page form with a rich text heading for each step, and tell Jess she'll split the steps in the editor.

### 3. Build the form
- Follow `form_spec.json` in order: the introduction first, then one step (or headed section) per entry in `steps`.
- Use `label`, `required`, and `helpText` exactly as written in the spec.
- Take radio, dropdown, and checkbox options from the property definitions fetched in step 1, never retyped.
- Map field types: `radio`, `multiple_checkboxes`, `single_line_text`, `multi_line_text`, `number`, `datepicker`, `email`.
- Add `ratingScaleHelpText` as a rich text block at the top of the Employer Engagement step.
- Use `thankYouMessage` as the inline thank-you message.

### 4. Verify and report
- GET the form back. Confirm it has 102 fields (`expectedFieldCount`) and the step-by-step counts below.
- Report the form's editor URL, the field count per step, and anything that couldn't be built through the API.

| Step | Fields |
| --- | --- |
| Chapter Information | 13 |
| Employer Engagement | 10 |
| Leadership & Governance | 11 |
| College Capacity | 12 |
| Student Recruitment Pipeline | 11 |
| Employer Recruitment Infrastructure | 11 |
| Resources & Ownership | 12 |
| Overall Readiness | 1 |
| Priority Action Plan | 15 |
| Confirm the Expansion Goal | 6 |

## Known open items (don't block the build)
- FAME still has to confirm that `starting_fall` and `returning_fall` should take the first- and second-year cohort answers. Build them as specified.
- HubSpot can't cap checkbox selections, so "select up to three" stays in the label.
