# ECOD explanation faithfulness evaluation — observed results

The supplied external LLM judge response has been validated. All 12 regular explanations received 3/3, and both controls failed their intended criterion. No disagreements were found between the judgments and an independent inspection of the recorded CSV evidence. This evaluates explanation faithfulness separately from anomaly detection performance, which the report evaluates using ROC-AUC and average precision.

## Provenance and validation

The user reports running the fixed, blinded `judge_prompt.txt` in an external chat and supplied the unchanged response in `judge_raw.txt`. This local completion step made no LLM call and did not generate or substitute judgments. The original response is preserved; its SHA-256 is recorded in `judgment_validation.json`.

**Judge: GPT-6 (exact model variant unavailable). Run date: 9 November 2026, Sydney local time (Australia/Sydney).** These details were supplied by the user and are recorded in `judge_metadata.json`. Time of day was not recorded.

Validation of the raw JSON response confirmed:

- Exactly 14 rows, with every expected case ID C001–C014 appearing once and no unknown IDs.
- Every attribution, numerical accuracy, and scope score is an integer 0 or 1.
- Every total equals the sum of its three criterion scores.
- Every row contains the required fields and a nonempty reason.

Original source-file hashes were unchanged. Each case was matched back to its source CSV by rank, with input row, actual label, full source record, recorded score, and all four contributions checked locally against the source CSVs and blinded inputs. Labels were used only for local verification, not to judge explanation faithfulness.

## Case preparation

Only existing `results/extensions/*_10pct_seed42_scores.csv` files were used. ECOD and dataset generation were not rerun. The report was not edited and nothing was published.

| Dataset | Scored rows N | Selected ranks |
| --- | ---: | --- |
| banknote | 200 | 1, 67, 134, 200 |
| synthetic_extreme | 400 | 1, 134, 267, 400 |
| synthetic_relationship | 400 | 1, 134, 267, 400 |

Selection used ranks 1, ceil(N/3), ceil(2N/3), and N. Preparation checked required columns, four finite nonnegative contributions, finite input values and scores, binary labels, unique input rows, contiguous ranks, descending scores, and contribution sums. The sum tolerance was `1e-9 + 1e-12 * abs(score)`; the largest absolute discrepancy was `2.7e-15`.

The 12 regular candidates used: “ECOD assigned this row an anomaly score of [score]. The largest contribution came from [feature], with [contribution].” All exactly tied maxima were derived directly from the unrounded contribution columns. Displayed numbers use three decimals; judge evidence preserves all recorded CSV digits.

Two controls reused real rows: one named an incorrect largest feature, and one added a claim that a high score proves the row is truly anomalous. Controls were mixed with regular cases before assigning neutral IDs. The judge saw only IDs, recorded scores, all four named contributions, explanations, and the fixed rubric. Dataset names, ranks, actual labels, expected scores, and control status were withheld.

## Regular-case results

Controls are excluded from every count below.

| Measure | Pass count | Percentage |
| --- | ---: | ---: |
| Attribution | 12/12 | 100% |
| Numerical accuracy | 12/12 | 100% |
| Scope | 12/12 | 100% |
| All three criteria (3/3) | 12/12 | 100% |

Regular case IDs: C001, C003, C004, C005, C006, C007, C008, C009, C010, C011, C013, C014.

## Controls, reported separately

| Case | Control | Attribution | Numerical accuracy | Scope | Total | Intended failure observed? |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| C002 | Incorrect largest feature | 0 | 0 | 1 | 1/3 | Yes: attribution |
| C012 | Unsupported proof of true anomaly status | 1 | 1 | 0 | 2/3 | Yes: scope |

C002 names variance and assigns it 5.521. The CSV records variance as 4.8283137373023015, while skewness and kurtosis tie for the maximum at 5.521460917862246 each. Its additional numerical failure is justified: the quoted maximum is numerically close to the actual maximum but is attached to the wrong feature. The rubric requires additional numerical claims, including numbers associated with named features, to match the evidence.

C012 correctly states the score and the tied feature_1/feature_3 contributions but adds “This high score proves the row is truly anomalous.” The recorded score and contributions do not support that conclusion, so its scope failure is justified.

## Independent evidence review and disagreements

**No scoring disagreements were found across the 14 cases.** All raw judgment scores were retained unchanged. Local evidence checks are an audit of the actual LLM response, not a replacement for it.

Each candidate was inspected against its source score and four contributions. The audit recomputed exact ties, compared the named feature set with all maxima, checked the stated total and contributions within 0.002, checked numerical values against each named feature, and inspected scope wording. All regular candidates passed these checks. The two regular tied-maximum cases were handled correctly: C003 names skewness and kurtosis, and C009 names feature_1 and feature_3. The judge's reasons are consistent with the corresponding CSV values and the two control errors. The independent per-case working audit and private case key remain in the original local project. The public package includes the original blinded inputs, raw judgments, scored CSV, source evidence, and validation totals.

## Limitations

Candidates were constructed using a fixed template directly from recorded contributions. The observed results support faithfulness of these constrained explanations for this sample; they do not establish reliability of freely generated explanations. The sample covers one split (seed 42), one anomaly prevalence (10%), three datasets, and four deterministically selected ranks per dataset. It is small and does not support broad claims across splits, prevalence levels, datasets, or the full score distribution. The two controls provide limited diagnostic checks rather than an estimate of judge accuracy. The exact GPT-6 variant was unavailable, and the supplied external chat's execution provenance cannot be independently confirmed from the raw response alone. No repeated judging runs or between-model agreement were evaluated.

## Report-ready paragraph

An LLM-as-judge evaluation using GPT-6 (exact variant unavailable) on 9 November 2026 (Sydney local time) assessed whether short ECOD explanations faithfully reflected recorded feature contributions, separately from anomaly detection performance measured by ROC-AUC and average precision. Twelve cases were selected at ranks 1, ceil(N/3), ceil(2N/3), and N from existing banknote, synthetic extreme, and synthetic relationship score files for seed 42 and 10% anomaly prevalence. All 12 fixed-template explanations passed attribution, numerical accuracy, and scope, receiving 3/3. Two additional controls failed their intended criteria: incorrect feature attribution and an unsupported claim that a high score proves true anomaly status. Independent comparison with the source CSV evidence found no scoring disagreements. These findings apply to this small, constrained sample and do not establish the reliability of freely generated explanations.

## Public artifacts

- `judge_prompt.txt` and `judge_inputs.json`: blinded rubric and cases.
- `judge_raw.txt`: unchanged supplied judge response.
- `judge_metadata.json`: model and date supplied by the user.
- `scored_cases.csv`: actual judge scores and reasons.
- `judgment_validation.json`: validation results, counts, controls, and raw-response hash.
- `preparation_validation.json`: source hashes and preparation checks.

The private local case key and working audit are intentionally excluded. Controls are identified above for analysis; use only the original judge prompt for any fresh blinded run. No hosted judge API or credentials are required to inspect these results.
