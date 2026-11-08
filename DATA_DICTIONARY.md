# Real participant dataset — source fields

The included `participants.csv` contains responses from **36 real participants**. Collection began with a smaller sample, then expanded with additional questions. Consequently, not every participant has the same sequence length or the same optional fields. Blank cells represent values not recorded in that field.

| Column | Meaning |
|---|---|
| `participant_id` | Anonymous participant number |
| `heads_tails` | Actual full sequence of imagined H/T choices; length varies |
| `sequence_length` | Recorded length of that sequence |
| `number_1_10_first` | First choice from 1–10; used in the app |
| `number_1_10_second` | Additional 1–10 choice if collected; not used in the current app |
| `number_1_100` | Choice from 1–100; used in the app |
| `count_to_10_trial_1_seconds` | Recorded timing result; preserved but not used in gameplay |
| `count_to_10_trial_2_seconds` | Additional timing result if collected; preserved but not used |
| `extra_number_unassigned` | Ancillary raw field; not used |
| `raw_number_entry` | Original number response representation |

**Six-flip normalization:** the app uses `heads_tails[:6]` for all 36 participant rows (provided at least six valid H/T characters). For 17 longer records, these are genuine recorded first six flips, not simulated observations. Full source data is retained.

**Missing data:** when a response is absent, the app should show unavailable instead of generating a value.

**Fields retained outside the app:** counting-to-ten measurements, second 1–10 choices, additional unassigned numbers, and raw number entries preserve the broader collection. The final app uses coin sequences, the first 1–10 choice, and the 1–100 choice. Timing is not a model feature: computer rounds have no corresponding counting task. Different sequence lengths and optional responses reflect the evolving collection; equal-length prefixes do not eliminate possible differences between collection stages.

**Limitations:** no population representativeness guaranteed; small n; possible participant selection biases and task instruction ambiguity. Add details on exactly when, where, and how consent was obtained before publishing.
