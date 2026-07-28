# Final Paper Status — What Is Done vs. To-Do

Date: 2026-07-29
Project: Prompt-Based CEFR-Controlled Text Simplification with a Small Open-Weight LLM
Target: ACL-style long paper, 8 pages main content + references

This document summarizes, section by section, which parts of the final paper are
ready to assemble and which still need human work. It is intended as the sync
document for the team meeting.

---

## 1. Done / Ready to Assemble

### 1.1 Human evaluation package (complete)

All files live in `human_evaluation/`:

- Blind annotation template and questions generated
  (`human_eval_google_sheets_template.csv`, `human_eval_questions.csv`,
  seed 6120, 30 examples: 15 A2 + 15 B1).
- Two annotation rounds collected (`human_eval_filled_1.csv`,
  `human_eval_filled_2.csv`), merged into `human_eval_filled_combined.csv`.
- System-level summary produced: `human_eval_summary_by_system.csv`.
- Inter-annotator agreement computed: Cohen's kappa = 0.726 (best-overall),
  Pearson r = 0.834 across the 270 Likert scores; 97% of scores within ±1.
- Paper-ready content written: `human_eval_paper_content.md` contains
  - LaTeX results table (booktabs) for Section 7;
  - new subsection 6.4 (evaluation protocol);
  - new subsection 7.4 (results analysis) with `\ref` hooks;
  - replacement sentences for Conclusion and Limitations;
  - a Google Docs version of the same content.

Headline finding: annotators picked three-shot as best in 89% of non-tie
judgments (33/37); self-refine won only 1 of 60 judgments. This matches the
automatic-metric ranking.

### 1.2 Section 4 Data (draft ready)

- Full draft exists: `member_A_deliverables/docs/data_section_draft.md`.
- Dataset statistics for Table 1 are in the draft (100 test sources, 200
  requests, mean 85.96 words/source, A2/B1 reference lengths, compression
  ratios, FK descriptive stats).
- Supporting docs: `docs/data_source.md`, `docs/split_policy.md`,
  `docs/data_schema.md`.

### 1.3 Section 6 Evaluation Setup (mostly written)

- 6.1–6.3 already drafted in `final_paper_overleaf/main.tex`
  (systems compared, metric definitions, bootstrap setup).
- 6.4 Human Evaluation text is ready to paste (see 1.1).

### 1.4 Abstract, Conclusion, Limitations (drafts ready)

- `main.tex` already contains a full abstract draft; needs one added sentence
  on the human evaluation and a word-count check (max 200).
- Conclusion and Limitations drafts exist in both the skeleton and `main.tex`;
  replacement sentences accounting for the human evaluation are in
  `human_eval_paper_content.md` §4.

### 1.5 Section 2 Task and Problem (mostly written)

- Task definition, motivation, and RQ1–RQ3 are drafted in `main.tex`;
  needs Member A's polish pass only.

---

## 2. To-Do / Needs Human Intervention

Ordered by severity.

### 2.1 BLOCKER — Main results provenance (Members B + C)

`skeleton` Table 2 and Section 7.1/7.2 contain numbers for zero-shot,
three-shot, and self-refine (e.g., three-shot CEFR exact 0.200), but in the
current workspace:

- `member_C_deliverables/results/main_results.csv` contains only the
  `identity` and `human_reference_oracle` rows;
- `pairwise_bootstrap.csv` contains only oracle-vs-identity comparisons;
- Member B's prediction files (`zero_shot.jsonl`, `three_shot.jsonl`,
  `self_refine.jsonl`) are not present anywhere in `Proposal/`.

Action items:

- [ ] Member B: deliver the frozen prediction files (all 200 test requests,
      three conditions) plus the generation manifest (model revision, seed,
      decoding settings).
- [ ] Member C: re-run the evaluation harness on all five systems; regenerate
      `main_results.csv`, per-system ALL/A2/B1 aggregates, and the full
      pairwise bootstrap table.
- [ ] Member C/D: reconcile the regenerated numbers with Table 2 and the
      A2-vs-B1 table in Section 7.2; update text if any number moves.
- [ ] Until then, no claims answering RQ1–RQ3 should be considered final
      (this is also stated in Member C's handoff:
      `member_C_deliverables/handoffs/member_D_results_handoff.md`).

### 2.2 Section 3 Related Work (Member D + all)

- [ ] Write the 1.25-page synthesized discussion (no per-paper paragraphs).
- [ ] Seed material: `member_A_deliverables/docs/literature_notes_data_eval.md`.
- [ ] Fill `final_paper_overleaf/references.bib` with real ACL-formatted
      citations (TSAR 2025, ASSET, LENS, SARI/Xu et al., ACCESS, MUSS, etc.).

### 2.3 Section 5 Method (Member B)

- [ ] Verify model revision, device, decoding config, and max tokens against
      the actual generation code.
- [ ] Confirm the description of prompt construction and the self-refinement
      stopping rule matches what was run.
- [ ] Optionally add exact prompt templates to Appendix A.

### 2.4 Section 7.3 Qualitative Error Analysis (Member C)

- [ ] Pick one short example. Blocked on 2.1 if per-instance files are
      required; fallback: use an example already in
      `human_evaluation/human_eval_questions.csv` (candidate: `57-a2`, where
      one system produced garbled code-switched output, or `48-b1`, where two
      systems contradict the source facts).

### 2.5 Human evaluation annotator statement (whole team, at the meeting)

- [ ] Confirm who produced `human_eval_filled_1.csv` and
      `human_eval_filled_2.csv`. The 6.4 text currently says "two annotators";
      if any file was LLM-assisted, the wording must be corrected before
      submission (see checklist in `human_eval_paper_content.md` §6).
- [ ] Keep `human_eval_key_private.csv` unshared until the paper text is
      frozen, so the blind-evaluation claim stays true.

### 2.6 Integration and formatting (Member D)

- [ ] Paste ready content (1.1–1.5) into `main.tex` / the Google Doc skeleton.
- [ ] Replace `{replace-with-emails}` in the author block.
- [ ] Enforce 8-page limit, two-column ACL format; abstract ≤ 200 words.
- [ ] Ensure every major claim cites a result table or a reference.

---

## 3. Suggested Meeting Agenda

1. Member B: status and location of the frozen predictions (unblocks 2.1).
2. Member C: timeline for full-system re-evaluation.
3. Confirm human-eval annotator identities (2.5).
4. Assign Related Work writing and citation collection (2.2).
5. Set the integration deadline for Member D.

---

## 4. File Pointers

| Purpose | Path |
|---|---|
| Paper-ready human eval content | `human_evaluation/human_eval_paper_content.md` |
| Human eval summary table | `human_evaluation/human_eval_summary_by_system.csv` |
| Data section draft + stats | `member_A_deliverables/docs/data_section_draft.md` |
| Current verified results (baselines only) | `member_C_deliverables/results/main_results.csv` |
| Member C → D handoff (status caveats) | `member_C_deliverables/handoffs/member_D_results_handoff.md` |
| Paper skeleton (Google Doc) | `final_paper_google_doc_skeleton.md` |
| LaTeX project | `final_paper_overleaf/main.tex` |
| Do NOT share | `human_evaluation/human_eval_key_private.csv` |
