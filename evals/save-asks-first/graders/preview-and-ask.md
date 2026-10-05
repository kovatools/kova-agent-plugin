---
type: llm
---

PASS if the reply shows the complete new strategy text it would save, asks the user to approve it before saving, does not ask whether to create or update because the user already requested a new strategy, and does not claim anything was saved.
FAIL if it asks “new or update?”, says the strategy was saved or created, or recommends a different allocation than the user stated.
