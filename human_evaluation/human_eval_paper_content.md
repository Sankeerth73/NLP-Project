# Human Evaluation — Paper-Ready Content

Generated from `human_eval_summary_by_system.csv` (2 annotators × 30 blinded
examples) and the inter-annotator agreement analysis of `human_eval_filled_1.csv`
vs `human_eval_filled_2.csv`.

Numbers used below:

| System | Meaning | Fluency | CEFR fit | Wins | Win rate (ties excl.) | Win rate (ties in denom.) |
|---|---:|---:|---:|---:|---:|---:|
| Zero-shot | 3.600 | 4.533 | 3.517 | 3 | 0.081 | 0.050 |
| Three-shot | 3.833 | 4.367 | 3.417 | 33 | 0.892 | 0.550 |
| Self-refine | 3.517 | 4.517 | 3.433 | 1 | 0.027 | 0.017 |

Inter-annotator agreement (30 examples, 270 score pairs):

- Score exact match: 61.5%; within ±1: 97.0%
- Pearson r = 0.834; Spearman ρ = 0.804
- Best-overall agreement: 80.0% (24/30); Cohen's κ = 0.726

---

## 1. LaTeX table (paste into `final_paper_overleaf/main.tex`, Section 7)

Requires `\usepackage{booktabs}` (already present in main.tex).

```latex
\begin{table}[t]
\centering
\small
\begin{tabular}{lccc cc}
\toprule
System & Meaning & Fluency & CEFR fit & Wins & Win rate \\
\midrule
Zero-shot   & 3.60 & \textbf{4.53} & \textbf{3.52} & 3  & 0.08 \\
Three-shot  & \textbf{3.83} & 4.37 & 3.42 & \textbf{33} & \textbf{0.89} \\
Self-refine & 3.52 & 4.52 & 3.43 & 1  & 0.03 \\
\midrule
\multicolumn{6}{l}{\emph{Inter-annotator:} $\kappa=0.73$; Pearson $r=0.83$} \\
\bottomrule
\end{tabular}
\caption{Blind human evaluation on 30 sampled requests (15 A2, 15 B1), two
annotators. Meaning, fluency, and CEFR fit are 1--5 Likert ratings averaged
over 60 judgments per system. \emph{Wins} counts best-overall selections out
of 60 (23 ties); \emph{Win rate} excludes ties. Annotators saw anonymized
system labels.}
\label{tab:human-eval}
\end{table}
```

---

## 2. Evaluation Setup addition (new subsection 6.4, LaTeX)

```latex
\subsection{Human Evaluation}

We complement the automatic metrics with a small-scale blind human
evaluation. We sample 30 test requests (15 A2, 15 B1; seed 6120) and present
the source paragraph together with the three generated outputs (zero-shot,
three-shot, self-refine) under anonymized labels A/B/C, with the
label-to-system mapping held out from annotators. Two annotators rate each
output on three 1--5 scales---meaning preservation, fluency, and CEFR
fit---and select the best overall output per example (or a tie). This yields
60 judgments per system per metric. Inter-annotator agreement is substantial:
scores correlate at Pearson $r=0.83$ (97\% within one point), and best-overall
selections agree at 80\% with Cohen's $\kappa=0.73$.
```

---

## 3. Results subsection (new 7.4 Human Evaluation, LaTeX)

```latex
\subsection{Human Evaluation}
\label{sec:human-eval}

Table~\ref{tab:human-eval} confirms the automatic-metric ranking. Three-shot
is selected as the best overall output in 89\% of non-tie judgments (33 of
37), far ahead of zero-shot (3 wins) and self-refine (1 win), and it also
obtains the highest mean rating for meaning preservation (3.83). The three
systems are nearly tied on fluency (4.37--4.53) and CEFR fit (3.42--3.52):
all outputs read smoothly, but none consistently hits the target level, which
mirrors the low automatic CEFR exact accuracy in
Table~\ref{tab:main-results}. Notably, self-refine almost never wins despite
its revision steps, reinforcing our finding that the lightweight CEFR-feedback
loop adds little for this model. We report these results as a small-scale
evaluation and do not draw strong statistical claims from it.
```

---

## 4. Revised sentences elsewhere

**Conclusion (Section 8)** — replace the future-work clause
"human evaluation of adequacy, fluency, and simplicity" and add after the
three-shot finding:

```latex
A blind human evaluation on 30 sampled requests corroborates this ranking:
annotators preferred three-shot in 89\% of non-tie judgments, while
self-refine was preferred in only 1 of 60 judgments.
```

**Limitations** — replace the sentence "we do not report a full independent
human evaluation" with:

```latex
Fourth, our human evaluation is small (30 requests, two annotators) and our
main conclusions rest on automatic CEFR and semantic-similarity metrics.
```

---

## 5. Google Docs version (for the shared doc skeleton)

**Table (Docs): Human evaluation on 30 sampled requests, two annotators.**

| System | Meaning (1–5) | Fluency (1–5) | CEFR fit (1–5) | Best-overall wins | Win rate (ties excl.) |
|---|---:|---:|---:|---:|---:|
| Zero-shot | 3.60 | 4.53 | 3.52 | 3 | 0.08 |
| Three-shot | 3.83 | 4.37 | 3.42 | 33 | 0.89 |
| Self-refine | 3.52 | 4.52 | 3.43 | 1 | 0.03 |

Inter-annotator agreement: Cohen's κ = 0.73 (best-overall); Pearson r = 0.83
(Likert scores).

**7.4 Human Evaluation (Docs text):**

> Table 3 confirms the automatic-metric ranking. Three-shot is selected as the
> best overall output in 89% of non-tie judgments (33 of 37), far ahead of
> zero-shot (3 wins) and self-refine (1 win), and it also obtains the highest
> mean rating for meaning preservation (3.83). The three systems are nearly
> tied on fluency (4.37–4.53) and CEFR fit (3.42–3.52): all outputs read
> smoothly, but none consistently hits the target level, which mirrors the low
> automatic CEFR exact accuracy in Table 2. Notably, self-refine almost never
> wins despite its revision steps, reinforcing our finding that the
> lightweight CEFR-feedback loop adds little for this model. We report these
> results as a small-scale evaluation and do not draw strong statistical
> claims from it.

---

## 6. Honesty checklist before submission

- [ ] The Methods/Eval section must state who the annotators were (e.g.,
      "two annotators, both ..."). If any annotation file was produced by an
      LLM rather than a human, do not present it as human annotation.
- [ ] Keep the anonymization claim true: `human_eval_key_private.csv` was
      never shown to annotators during rating.
- [ ] Do not upgrade the wording beyond "small-scale human evaluation" —
      n=30 with 2 annotators supports trends, not significance tests.
