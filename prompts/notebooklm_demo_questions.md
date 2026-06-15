# NotebookLM Demo Questions

Upload `demo/notebooklm_sources/INC-2026-0001_callback_timeout_notebooklm_source.md`
to a NotebookLM notebook, then ask questions like these.

## Similar incident and restoration queries

- What happened in incident INC-2026-0001?
- Which service was impacted and what customer symptoms were reported?
- What restoration actions were performed, and who owned them?
- What was the fastest mitigation used in this incident?
- Which teams were involved in resolving the incident?
- What evidence supports the callback timeout diagnosis?
- What root cause was identified?
- What follow-up actions remained after restoration?

## Active incident assistant queries

- We are seeing HTTP 504 timeout errors from the bank callback endpoint. What
  should we investigate first based on this incident history?
- Users cannot complete cash-in transactions and callback responses are delayed.
  What similar evidence exists in the uploaded incident source?
- Which restoration steps were completed before service recovery?
- What should the incident manager ask the Middleware and Network teams to
  verify?

## Grounding checks

- List the exact transcript timestamps used for your answer.
- Show the source references for each recommendation.
- If the source does not contain evidence for a recommendation, say so clearly.
