# Minimum 15 Test Cases

| ID | Case | Expected |
|---|---|---|
| TC01 | Valid fresher plan | Plan returned |
| TC02 | Unknown city | Error / rejected |
| TC03 | Unknown education | Model handles/rejects according to API policy |
| TC04 | Unknown job role | Model handles/rejects according to API policy |
| TC05 | Timeline 0 | Rejected |
| TC06 | Negative timeline | Rejected |
| TC07 | Saving -1% | Rejected |
| TC08 | Saving 101% | Rejected |
| TC09 | Saving 0% | Capacity = 0; shortfall shown |
| TC10 | Saving 100% | Capacity = salary |
| TC11 | High goal requirement | Shortfall shown |
| TC12 | 3-year goal | Short-term category |
| TC13 | 7-year goal | Medium-term category |
| TC14 | 8-year goal | Long-term category |
| TC15 | 1-year inflation | Current × 1.06 |
| TC16 | RAG unknown question | “Information unavailable…” |
| TC17 | Prompt injection text | Request is blocked; tools/system instructions cannot be bypassed |
| TC18 | Multiple goals | Each goal calculated separately and total combined |