# Phase 0 artifact — precision@10

Corpus: 585 markdown notes -> 596 heading-level chunks, 11,958 terms, avgdl 194.
Ranking: BM25 (k1=1.5, b=0.75), no stemming, no stopword removal.
Judgments: single judge, binary relevance, judged against the stated need.

| Query | Need | P@10 |
|---|---|---|
| `eeg neurofeedback` | My own EEG work and interest in the area | 0.8 |
| `political philosophy` | My interest in it and how I got there | 0.6 |
| `build system phases` | My attempts at the build system and where it stands | 0.5 |
| `audio signal processing eeg` | Notes where I worked out how audio DSP transfers to EEG | 0.4 |
| `frustrating internship` | What I didn't like about my internships | 0.1 |

## What this table cannot see

- **Rank position within the top 10.** Precision@k is set-based: a relevant
  document at rank 1 counts the same as one at rank 10. Instrument: Average
  Precision / MAP (IIR 8.4).
- **Relevant documents outside k.** That is recall (8.3), which requires
  judging the whole corpus. Real systems approximate it by pooling (8.2).
- **The choice of k itself.** A precision-recall curve (8.4) shows the
  tradeoff across all k instead of fixing one.
- **Judgment reliability.** One judge, unmeasured. Kappa (8.5) would test
  whether two judges agree.
- **Statistical significance.** Five queries is too few to say whether the
  differences reflect the system or the query sample.

## Observed failure mode

Scores track lexical overlap between the need's vocabulary and the documents'.
`frustrating internship` scores 0.1 because nothing written about disliking an
internship uses the word "frustrating." `audio signal processing eeg` scores 0.4
because six of ten hits were career and networking documents -- written to
*claim* the audio/EEG transfer, so they name every relevant term, while the
document that actually works the transfer out ranked third.

BM25 rewards documents that talk about a topic over documents that do the thing.
