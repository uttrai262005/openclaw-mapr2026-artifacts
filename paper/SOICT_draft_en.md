# Draft Paper (EN) — OpenClaw Rubric-based Grading (SOICT/CCIS style)

> Venue target: SOICT (Springer CCIS template, single-blind).  
> Language: English (required by SOICT in recent years).  

## Title (choose one)
1. **An Auditable Agentic LLM Pipeline for Rubric-Based Grading: Evidence from a Real E-commerce Course Dataset**
2. **Rubric-Grounded Automated Grading with OpenClaw: Reliability Analysis of Single-Agent vs Multi-Agent Scoring**
3. **From Classroom Submissions to Research-Ready Scores: An OpenClaw-Based LLM Grading System with Audit and QWK Evaluation**

## Abstract (draft)
Large enrollment courses rely on rubric-based assessment to ensure transparency and consistency, but grading is labor-intensive and often delays feedback. Recent large language model (LLM) graders are promising, yet prior studies frequently lack (i) end-to-end, auditable pipelines for heterogeneous real submissions, and (ii) reliability-first evaluation contextualized by human inter-rater agreement. We present an agentic grading pipeline implemented with the OpenClaw framework and apply it to four assignments in an undergraduate e-commerce introduction course at UIT. The pipeline includes dataset normalization, optional OCR for scanned documents, incremental result writing, and automated auditing to guarantee a one-to-one mapping between submissions and exported scores.
We evaluate grading quality using Quadratic Weighted Kappa (QWK), MAE, and Pearson correlation. Two human graders independently score each submission; ground truth is defined as the mean of the two scores. We compare a single-agent configuration (Phase 1) and a multi-agent configuration (Phase 2) that decomposes grading into content/structure/language graders and aggregates scores via a chairman agent.
Across assignments, we observe that multi-agent grading does not consistently improve agreement with human scores; in our dataset, the single-agent configuration achieves higher QWK against human-mean ground truth on all four assignments in the human-graded sample (e.g., BT3: 0.827 vs. 0.613; BT4: 0.720 vs. 0.517). We further show that Phase 2 exhibits systematic score shifts relative to Phase 1 (three assignments skew lower, one skews higher), suggesting calibration and aggregation as critical factors. We discuss failure modes and practical deployment considerations for rubric-grounded automated grading.

**Keywords:** automated grading, rubric-based assessment, agentic AI, LLM, OpenClaw, reliability, QWK

## 1 Introduction
### 1.1 Motivation
Rubric-based grading supports fairness and consistent evaluation, but it becomes a bottleneck in large classes. In real settings, submissions are heterogeneous (DOCX/PDF/TXT; scanned artifacts), and instructors require auditable outputs, deterministic scoring rules, and complete exports for administration and research.

### 1.2 Gap
Despite rapid progress in LLM-based assessment, existing work often (i) evaluates on limited or sanitized datasets, (ii) omits an end-to-end pipeline that ensures auditability and one-to-one submission-to-score mapping, and (iii) reports performance without contextualizing results relative to human inter-rater agreement. Consequently, it remains unclear when agentic multi-step grading improves reliability over a single-pass grader under realistic classroom constraints.

### 1.3 Contributions
- **C1 (System):** We build an auditable OpenClaw-based pipeline for rubric-grounded grading, covering normalization → OCR (when needed) → grading → incremental export → automated auditing.
- **C2 (Dataset/Artifacts):** We curate a clean, research-ready dataset of four rubric-based assignments from a real undergraduate e-commerce course (UIT), with validated one-to-one mapping between submissions and grading outputs.
- **C3 (Reliability-first evaluation):** We report human inter-rater QWK and benchmark two AI configurations against a ground truth defined as the mean of two human graders, using QWK/MAE/Pearson.
- **C4 (Insights):** We analyze why multi-agent grading can underperform single-agent grading, focusing on calibration mismatch, aggregation smoothing, and surface-feature bias.

## 2 Related Work (outline)
- Automated short answer/essay scoring and feedback generation
- Rubric-based and criterion-level scoring with LLMs
- Reliability in educational measurement; QWK as agreement metric
- Agentic workflows and multi-agent decomposition

## 3 Method
### 3.1 Dataset pipeline and auditability
**Inputs:** student submissions (multiple file types), rubric documents.
**Steps:**
1. Normalize and validate submission list (deduplication, canonical IDs).
2. Extract text from DOCX/PDF/TXT (best-effort).
3. OCR for scanned PDFs/images (notably for CV submissions).
4. LLM grading based on rubric.
5. Deterministic rounding: per-criterion to 0.25; total to 0.5 (0..10).
6. Incremental write to XLSX.
7. Automated audits: missingness, duplicates, score constraints.

### 3.2 Phase 1: Single-agent grading
Describe prompt structure: rubric injection, required outputs (criterion scores + total + short feedback).

### 3.3 Phase 2: Multi-agent grading (OpenClaw skill giang-vien-v2)
- Three graders run in parallel: content, structure, language.
- A chairman agent aggregates by averaging per criterion; flags veto when grader spread exceeds a threshold; applies rounding rules.

## 4 Experimental Setup
### 4.1 Data
Four assignments (BT1–BT4) with rubric-based scoring.

### 4.2 Human grading and ground truth
Two independent human graders (Ng1, Ng2). Ground truth GT = (Ng1 + Ng2)/2.

### 4.3 Metrics
- **Inter-rater agreement:** QWK(Ng1_int, Ng2_int), where *_int = round(2x) as integer.
- **AI vs GT:** QWK(P*_int, GT_int), MAE(|P* − GT|), Pearson r(P*, GT).

## 5 Results
We report results on (i) a human-scored subset (30 submissions per assignment) used to compute human agreement and AI-vs-human metrics, and (ii) the full dataset outputs (N=123–137 per assignment) used to analyze Phase 2 vs Phase 1 score shifts and stability signals (veto/spread).

### 5.1 Human inter-rater reliability (upper bound)
Table 1 reports Quadratic Weighted Kappa (QWK) between two human graders. Human agreement is moderate to substantial in our setting, which provides a realistic upper bound for automated graders.

- BT1: QWK = **0.698**
- BT2: QWK = **0.684**
- BT3: QWK = **0.671**
- BT4: QWK = **0.628**

### 5.2 Phase 1 vs Phase 2 against human-mean ground truth
Table 2 compares Phase 1 (single-agent) and Phase 2 (multi-agent) against GT = (Ng1+Ng2)/2 on the human-scored subset.

**Key finding:** Phase 1 achieves higher agreement than Phase 2 on all four assignments.

- **BT1:** P1 QWK **0.484** vs P2 QWK **0.043**
- **BT2:** P1 QWK **0.331** vs P2 QWK **-0.002**
- **BT3:** P1 QWK **0.827** vs P2 QWK **0.613**
- **BT4:** P1 QWK **0.720** vs P2 QWK **0.517**

Phase 1 also consistently attains higher Pearson correlation with GT. On MAE, Phase 2 can be lower in some cases, but QWK reveals that Phase 2 more frequently disagrees on ordinal distinctions important for rubric scoring.

### 5.3 Phase 2 induces systematic score shifts (full dataset)
Using the full exported outputs (Phase 1 and Phase 2) we quantify whether Phase 2 is systematically harsher or more lenient than Phase 1.

- **BT1 (N=137):** mean(P2−P1) = **−0.836** (median = −1)
- **BT2 (N=129):** mean(P2−P1) = **+1.787** (median = +2)
- **BT3 (N=123):** mean(P2−P1) = **−0.943** (median = −1)
- **BT4 (N=131):** mean(P2−P1) = **−0.889** (median = −1)

This pattern suggests that multi-agent grading introduces calibration differences that are assignment-dependent rather than uniformly improving alignment.

### 5.4 Stability signals: veto rate and grader spread
Phase 2 produces two additional signals: a veto flag (triggered when graders differ substantially) and a spread score.

- **BT1:** veto rate ≈ **0.993**, mean spread ≈ **5.15**
- **BT2:** veto rate ≈ **0.922**, mean spread ≈ **3.39**
- **BT3:** veto rate ≈ **0.772**, mean spread ≈ **2.65**
- **BT4:** veto rate ≈ **0.061**, mean spread ≈ **1.13**

The very high veto rates on BT1–BT3 indicate frequent disagreement among specialized graders, consistent with the observation that naive per-criterion averaging can harm agreement with human scores.

### 5.5 Why single-agent can outperform multi-agent (evidence-based hypotheses)
We interpret the above results through three mechanisms.

1) **Aggregation smoothing and calibration mismatch.** Averaging per-criterion across graders can regress scores toward the mean or amplify severity differences if graders are not calibrated to a shared scoring policy.

2) **Systematic score shift (bias).** The observed assignment-specific mean(P2−P1) indicates that Phase 2 behaves as a different rater with its own bias (harsher in BT1/3/4, more lenient in BT2). Without explicit calibration, this bias reduces agreement with human-mean GT.

3) **Surface-feature sensitivity vs rubric intent.** A language-focused grader can overweight writing mechanics and formatting even when rubric criteria emphasize factual completeness, sourcing, and domain-specific correctness (particularly BT1–BT2). This can change ordinal comparisons and lower QWK even if MAE does not increase proportionally.

## 6 Discussion, Practical Recommendations, and Threats to Validity
### 6.1 Practical recommendations for improving multi-agent grading
Based on our findings, we recommend three low-cost modifications before expecting gains from a multi-agent setup.

- **R1: Calibrate grader severity using anchor papers.** Select a small set of anchor submissions with stable human scores; have each specialized grader score them; estimate per-grader offset/scale (or isotonic mapping) to align to a shared rubric scale before aggregation.

- **R2: Use robust aggregation instead of simple mean.** Replace per-criterion mean with median or trimmed mean to reduce the impact of outlier severity. Alternatively, learn aggregation weights constrained by rubric maxima.

- **R3: Rubric-aligned authority weighting.** For assignments where rubric emphasizes factual correctness and sourcing (BT1–BT2), downweight language/style judgments; for CV/essay-heavy tasks (BT3–BT4), increase the role of structure/language.

### 6.2 Threats to validity
- **Ground truth definition:** GT is the mean of two graders, not an absolute truth.
- **External validity:** data comes from a single course and institution.
- **Rubric ambiguity and grader drift:** both humans and LLM graders may interpret criteria differently.
- **Privacy and ethics:** student submissions are sensitive; we do not store chain-of-thought and recommend releasing only anonymized derived artifacts.

## 7 Conclusion
We introduced an auditable OpenClaw-based pipeline for rubric-grounded grading and curated a clean dataset from a real undergraduate course. Using reliability-first evaluation, we found that a single-agent grader achieved higher agreement with human scores than a multi-agent grader, and that the multi-agent setup induced assignment-dependent score shifts and frequent grader disagreement. We outline practical calibration and aggregation strategies needed for multi-agent grading to realize its potential in real classroom deployments.

## Appendix (optional)
- Prompts (anonymized)
- Additional tables/plots
