# RepairScope boundary

User action → commit-pinned snapshot report → independent complete semantic extraction → exact substantive validator comparison → all cardinality repairs → append-only Boolean query answers.

The contract owns the immutable source commitment and finite rosters, independent source acquisition and interpretation, a complete repair family, and query results with witnesses and counterexamples. External publishers own the reports; consensus does not establish custody truth. No frontend is included.

Facts have schema Custody(asset, holder, site). Fixed functional dependencies are asset → holder and holder → site. A repair is a **maximum-cardinality consistent subset of distinct asserted tuples**, not an arbitrary inclusion-maximal subset. Duplicate reports preserve provenance but cannot increase a tuple's weight.

All source records receive ASSERTED, OMIT, or UNKNOWN. UNKNOWN blocks the whole snapshot as REVIEW; it is never silently deleted. OMIT is restricted to no effective assertion, such as withdrawn drafts or forecasts. Contradictions across records remain facts for repair computation.

Each query is an existential conjunction of one to three triple patterns. Constants come from typed fixed rosters. A variable joins occurrences in the same column type. Constants may be repeated; one tuple may satisfy multiple atoms. CERTAIN means every C-repair satisfies the query, POSSIBLE means some but not all, IMPOSSIBLE means none. Query results are relative to this finite closed-world snapshot and chosen dependencies.

A query may be CERTAIN even if no individual fact is certain: alternative custodians can all place an asset at the same site. Evaluating only the intersection of repairs would lose this answer. Multi-atom joins retain within-repair correlations.

Limits: ten source rows / distinct facts, at most 1,024 candidate subsets, three atoms, six typed variables, sixteen stored query receipts. The permissionless evaluate view remains available after the append-only journal fills; strangers can consume journal slots but cannot block evaluation. Empty known database has one empty repair; every nonempty conjunctive query is IMPOSSIBLE. No arbitrary user code, floats, external payments, certificate consumption, owner proposals or mutable graph.

Validators re-fetch exact bytes, verify SHA-256 and the complete roster/schema, independently extract every status and named field, compare all consequential fields exactly, and audit the leader's quotes against full texts. Quotes may differ; substantive decisions cannot. A malformed model answer gets one repair attempt then fails; validators never agree on model failure.

References: [GenLayer equivalence principle](https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle); [database repair foundations, Wijsen](https://sigmodrecord.org/publications/sigmodRecord/1909/pdfs/03_Principles_Wijsen.pdf). This implements a bounded onchain CQA primitive, not a new database repair theory.
