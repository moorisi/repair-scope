# RepairScope

A standalone GenLayer consistent-query oracle over contradictory prose records.

Consensus interprets full fetched reports into custody tuples. The deterministic core preserves every maximum-size subset satisfying asset → holder and holder → site. Permissionless conjunctive queries distinguish CERTAIN, POSSIBLE and IMPOSSIBLE with source provenance, witness assignments and counterexample repairs.

This is a new relational repair mechanism, not a renamed proposal graph, majority fact vote, auction or service certificate.

## Local checks

```sh
pip install -r requirements-dev.txt
genvm-lint download --version v0.2.16
genvm-lint check contracts/repair_scope.py --json
python -m pytest tests/direct -q
node --test tests/rpc-preflight.test.cjs
```

See [architecture](docs/architecture.md), [contract](contracts/repair_scope.py), and [scenario fixtures](fixtures). Synthetic custody narratives demonstrate finite-database semantics, not physical custody or publisher honesty.

Generic encrypted CLI / receipt transport is reused under MIT from previous projects; this repository's repair engine, query evaluator, tests, fixtures and state oracles implement a distinct mechanism. The database algorithm is established CQA theory, explicitly credited in the architecture note.
