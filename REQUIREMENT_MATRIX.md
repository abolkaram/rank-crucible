# Requirement matrix

| Requirement | Mechanism | Status |
|---|---|---|
| Consensus-bound preference mapping | strict full-ranking normalization | PASS: forged ranking rejected |
| Complete canonical output | one permutation per submitted statement | PASS: malformed permutation rejected |
| Deterministic collective result | pairwise matrix and unique Condorcet test | PASS: winner and cycle tested |
| Authorization and liveness | frozen voters, one statement, expired permissionless paths | PASS: targeted tests |
| Exact deployed source | transaction source comparison | PASS: exact byte match |
