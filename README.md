# Setup

1. In the FAME HubSpot portal, create a private app (Settings → Integrations → Private Apps) with these scopes:
   - `forms`
   - `crm.schemas.custom.read`
   - `crm.objects.custom.read`
   - `crm.schemas.custom.write` (only needed if you approve fixing text field types)
2. Put `CLAUDE.md` and `form_spec.json` in one folder.
3. In a terminal in that folder, run `export HUBSPOT_ACCESS_TOKEN=your-token`, then start `claude`.
4. Paste this prompt:

> Read CLAUDE.md and form_spec.json, then build the Chapter Readiness Assessment form following the steps in CLAUDE.md. Start with step 0 and ask me how chapters should be matched.

Claude Code will stop to ask before changing any property and never publishes the form.
