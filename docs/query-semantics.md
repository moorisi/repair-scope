# Query and repair examples

RepairScope stores a finite relation `Custody(asset, holder, site)`. It does not ask an LLM whether a query should pass. Consensus only interprets source records; the database and query engine then use exact finite mathematics.

## Correlation

Four different assertions say Amber is held by either Blue or Red at North, and Bronze is held by either Blue or Red at North. No assertion supersedes another. Every maximum repair contains one assertion for each asset, giving four repairs.

- `exists h: Custody(Amber,h,North)` is CERTAIN even though the intersection of repairs contains no tuple.
- `exists h: Custody(Amber,h,North) AND Custody(Bronze,h,North)` is POSSIBLE: two repairs share a holder and two do not.
- `exists a,h: Custody(a,h,South)` is IMPOSSIBLE relative to this snapshot.

A witness includes a complete repair index and the matching fact indices / variable bindings. A counterexample is an actual maximum repair where the query has no assignment.

## Maximum versus maximal

The cardinality fixture asserts:

1. Amber / Red / South.
2. Bronze / Red / North.
3. Copper / Red / North.
4. Amber / Blue / South.
5. An additional copy of assertion 2.
6. A withdrawn draft.
7. A future forecast.

After semantic interpretation and tuple deduplication there are four distinct asserted facts. The singleton containing assertion 1 cannot be extended without breaking a dependency: it is inclusion-maximal. It is excluded by **maximum-cardinality** semantics because assertions 2, 3 and 4 form a consistent size-three repair.

The duplicate remains in `origins` but adds no vote or score. The withdrawn draft and forecast remain auditable in the assessment as OMIT and add no tuple. Amber / Red is IMPOSSIBLE among the chosen C-repairs, despite being one of the original assertions. This is a consequence of the explicit repair policy, not a claim that the assertion is physically false.

## Unresolved source

The third fixture has two complete assertions and an unresolved Copper record. UNKNOWN causes REVIEW for the complete snapshot. No answer is computed from a conveniently truncated database, including queries that mention only the apparently complete assets.

## Interface

`compile()` is permissionless and succeeds once. It fetches and interprets the immutable report in consensus, then stores the complete repair family.

`evaluate(atoms)` returns an answer without changing state. `query(atoms)` appends the same answer to the public journal, with at most sixteen entries. Duplicate queries are permitted. Evaluation remains available if other users fill the journal.

Each atom is a three-string array. Constants must occur in the corresponding fixed roster. Variables begin with `?`, use lowercase letters/digits, and may be reused within the same column type. Repeated variables join across atoms. There is no cross-column coercion, negation, distinctness constraint, free variable projection, arbitrary SQL or external code execution.

The empty known relation has one empty repair. Every accepted query contains at least one atom and is therefore IMPOSSIBLE on that relation. REVIEW differs from IMPOSSIBLE. Repair counts are logical alternatives, not independent evidence votes or calibrated probabilities; a query true in two of four repairs does not receive a 50% truth confidence.
