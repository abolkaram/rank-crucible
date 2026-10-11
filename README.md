# Rank Crucible

Scores can manufacture precision. Rank Crucible asks a narrower question: does one option beat every rival head to head?

A conductor freezes three to seven options, three to nine voter wallets, and a collection window. Each voter submits one preference statement in ordinary language. Validators independently turn every submitted statement into a complete option permutation. Contract code builds the pairwise matrix and recognizes a winner only when exactly one option defeats every other option.

The terminal record is `DECIDED` with a unique Condorcet winner or `CYCLE` with the disagreement intact. If fewer than three statements arrive, anyone may close the expired ballot as `INCOMPLETE`. Live voter wallets are operator-controlled role fixtures, not independent people.

```bash
genvm-lint contracts/contract.py
python -m pytest -q
```

## Live tally

- Contract: [`0x638d0b1CCB1C35400888A98A5e1E56158b344187`](https://explorer-studio.genlayer.com/address/0x638d0b1CCB1C35400888A98A5e1E56158b344187)
- Reviewed source: [`37d3779`](https://github.com/abolkaram/rank-crucible/tree/37d3779b2b7d488a61a275367f13dbfd964a5d1c)
- Live ballot: `VOTE-1791759399`, state `DECIDED`, winner `North Hall`.
- Verification: finalized, majority agree, successful execution, exact deployed-source match.
