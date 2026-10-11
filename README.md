# Rank Crucible

Scores can manufacture precision. Rank Crucible asks a narrower question: does one option beat every rival head to head?

A conductor freezes three to seven options, three to nine voter wallets, and a collection window. Each voter submits one preference statement in ordinary language. Validators independently turn every submitted statement into a complete option permutation. Contract code builds the pairwise matrix and recognizes a winner only when exactly one option defeats every other option.

The terminal record is `DECIDED` with a unique Condorcet winner or `CYCLE` with the disagreement intact. If fewer than three statements arrive, anyone may close the expired ballot as `INCOMPLETE`. Live voter wallets are operator-controlled role fixtures, not independent people.

```bash
genvm-lint contracts/contract.py
python -m pytest -q
```
