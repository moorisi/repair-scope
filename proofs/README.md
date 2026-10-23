# RepairScope — StudioNet scenario proofs

Three independent gasless StudioNet instances, chain **61999**. All **24 receipts** finalized with **MAJORITY_AGREE**: **12 successful executions** and **12 intentional ERROR rejections**. Every rejection has its exact returned error bytes and complete unchanged state checked.

Contract SHA-256: `464ded37aa4232612c0aa555050b1248ff716502f75941b83ccc6d49c18f2aeb`. Deployed source revision: `eb874e54d0044ffef1d62572a57eeb3125795f87`. Fixture revision: `b551cd83c7e549b6d2b3fd714c48f94d17b196a7`. The main source is byte-for-byte equal to deployment calldata and fresh contract code in each completed workflow.

| Scenario | Contract explorer | Deployment | Result |
|---|---|---|---|
| correlation | [0x5661ABdb46ceB9601c1a4b371990F4f0cB990F91](https://explorer-studio.genlayer.com/address/0x5661ABdb46ceB9601c1a4b371990F4f0cB990F91) | [deploy](https://explorer-studio.genlayer.com/tx/0xc8253dfb250f8d952a713eb4dc4e254c57537a7f50821363e41f81c73cdb0f3a) | Four size-two repairs; no certain tuple; queries CERTAIN / POSSIBLE / IMPOSSIBLE. |
| cardinality | [0x13cFc89dA81DC157d813f7A3ADF7b7220daf7E08](https://explorer-studio.genlayer.com/address/0x13cFc89dA81DC157d813f7A3ADF7b7220daf7E08) | [deploy](https://explorer-studio.genlayer.com/tx/0xa018c8383cbbc1a400abc8b8b70217308790a7301883d5dfc5fb4264e102167b) | One size-three repair; duplicate provenance retained; draft and forecast omitted; queries IMPOSSIBLE / CERTAIN / CERTAIN. |
| unresolved | [0x1797DDaa393F1ABa72c2230A74c9c35FC0881BDD](https://explorer-studio.genlayer.com/address/0x1797DDaa393F1ABa72c2230A74c9c35FC0881BDD) | [deploy](https://explorer-studio.genlayer.com/tx/0x8cc091fbf93543a1bb6796500b65f498fc6475d7c62c5f838ae2673b8c78be43) | REVIEW preserves record-3 uncertainty; all three query attempts rejected without state changes. |

## Every signed receipt

Votes include the leader and all recorded validators. Idle is not agreement. The correlation compilation had **3 agree / 2 disagree / 0 idle**; this is a strict majority, not unanimity. Other receipts also preserve idle votes.

| Call | Transaction | Execution | Agree | Disagree | Idle |
|---|---|---|---:|---:|---:|
| correlation-deployment | [tx](https://explorer-studio.genlayer.com/tx/0xc8253dfb250f8d952a713eb4dc4e254c57537a7f50821363e41f81c73cdb0f3a) | SUCCESS | 3 | 0 | 2 |
| correlation-reject-before-compile | [tx](https://explorer-studio.genlayer.com/tx/0x54920d86dad9bc66801c8de1fadb863e13433765f1419270bd10f55aa56771f4) | ERROR | 3 | 0 | 2 |
| correlation-compile | [tx](https://explorer-studio.genlayer.com/tx/0x86aa9e48d66218487e698afd48a99f7df919201168e0018d57e05868518a6d05) | SUCCESS | 3 | 2 | 0 |
| correlation-query-1 | [tx](https://explorer-studio.genlayer.com/tx/0x76e969e5a1f7b8e7ad5fea0f54f3f65277fe774043550533f4c456b7671a44f5) | SUCCESS | 3 | 0 | 2 |
| correlation-query-2 | [tx](https://explorer-studio.genlayer.com/tx/0xf79b20a76e6871ab8369cf922ae38a44a655b0b1d343febf1cd3c5937426be76) | SUCCESS | 3 | 0 | 2 |
| correlation-query-3 | [tx](https://explorer-studio.genlayer.com/tx/0xf9d2c0b05760b4004c9830c21d41cd5bc960f29ca6035854c83c1bb5ef96f952) | SUCCESS | 4 | 0 | 1 |
| correlation-reject-repeat-compile | [tx](https://explorer-studio.genlayer.com/tx/0xaea46b05fd16829c73885330c13e05b4a3a3dff0fe1950398eb521f25db02375) | ERROR | 5 | 0 | 0 |
| correlation-reject-invalid-query | [tx](https://explorer-studio.genlayer.com/tx/0xfe4cb1d8fefc7eb7f3628c6a3a4711efe40167ebb11f93957a35369d2052fd7b) | ERROR | 3 | 0 | 2 |
| cardinality-deployment | [tx](https://explorer-studio.genlayer.com/tx/0xa018c8383cbbc1a400abc8b8b70217308790a7301883d5dfc5fb4264e102167b) | SUCCESS | 3 | 0 | 2 |
| cardinality-reject-before-compile | [tx](https://explorer-studio.genlayer.com/tx/0x5092cc27167a295a6a340596c6a83b1481111c20dedecfd226ce657795ff0c67) | ERROR | 3 | 0 | 2 |
| cardinality-compile | [tx](https://explorer-studio.genlayer.com/tx/0xaef459f2255067a2e139b632acbb67d4360b7277098f5378b8cf80041340dc0c) | SUCCESS | 3 | 0 | 2 |
| cardinality-query-1 | [tx](https://explorer-studio.genlayer.com/tx/0x95fa0d6c71a7ef29bad59acda25dd515e8a7708dd45e6ad096359f7174dc63b5) | SUCCESS | 3 | 0 | 2 |
| cardinality-query-2 | [tx](https://explorer-studio.genlayer.com/tx/0x0f91883069cd5196f00494ee4092d422fa01852fa2bc4a7f7d75553c3a305667) | SUCCESS | 3 | 0 | 2 |
| cardinality-query-3 | [tx](https://explorer-studio.genlayer.com/tx/0x41dda24a51becef88c4affd47259ab1ccf7cc6d0f5c46272b1d6999fba7c7277) | SUCCESS | 3 | 0 | 2 |
| cardinality-reject-repeat-compile | [tx](https://explorer-studio.genlayer.com/tx/0x4c9588d5c2edb4f31efdd1d776d91c9b7172b5d169016d03b23b624fe0513a27) | ERROR | 3 | 0 | 2 |
| cardinality-reject-invalid-query | [tx](https://explorer-studio.genlayer.com/tx/0x0070d449c3527479f9bc95314862cbc79f2344209d145408cda361448b72e023) | ERROR | 3 | 0 | 2 |
| unresolved-deployment | [tx](https://explorer-studio.genlayer.com/tx/0x8cc091fbf93543a1bb6796500b65f498fc6475d7c62c5f838ae2673b8c78be43) | SUCCESS | 3 | 0 | 2 |
| unresolved-reject-before-compile | [tx](https://explorer-studio.genlayer.com/tx/0x2d7cc4384afc92debf341fb80a00ba7754904cff908ed2907e795fa6316d0664) | ERROR | 3 | 0 | 2 |
| unresolved-compile | [tx](https://explorer-studio.genlayer.com/tx/0x2aafa282145fad48a864b5d3351a61673d2ce2e85c780172c5ab34614bd79e59) | SUCCESS | 3 | 0 | 2 |
| unresolved-query-1 | [tx](https://explorer-studio.genlayer.com/tx/0xc7ff267a362adb375f0df8dbfa1163a7c146d9e84de03ed3496f4762ba3b563f) | ERROR | 5 | 0 | 0 |
| unresolved-query-2 | [tx](https://explorer-studio.genlayer.com/tx/0x62acf815792929a8bd312483f923a9355316136aafa5f1af11d3e75dc536db90) | ERROR | 3 | 0 | 2 |
| unresolved-query-3 | [tx](https://explorer-studio.genlayer.com/tx/0x1b4d4c6fd8530199fdfae45ba4cb01ab870027a9c12578e4b40c37f076f15163) | ERROR | 3 | 0 | 2 |
| unresolved-reject-repeat-compile | [tx](https://explorer-studio.genlayer.com/tx/0x62ac26038db1deb96f499b7f2a45a02705bc23b0e3ee517d083e273b7093009a) | ERROR | 3 | 0 | 2 |
| unresolved-reject-invalid-query | [tx](https://explorer-studio.genlayer.com/tx/0xcf9e5d0ce6b7e00d84374bbb58e9fbf9bb8c7640e3572c23660029bc9d689271) | ERROR | 3 | 0 | 2 |

## Verification and provenance

[Merged journal](transactions.json), [full verification](verification.json), [scenario provenance](provenance.json), [complete signed traces](correlation-trace.json) and individual receipt JSON files are committed alongside this page. The verifier decodes actual calldata using the SDK, checks sender/target, code bytes, complete vote membership, exact expected errors, full state before/after every call, every maximum repair, and each query witness/counterexample. Fresh checks re-fetch source and complete state and compare the evaluate view with persisted answers.

- [correlation workflow](https://github.com/moorisi/repair-scope/actions/runs/39945021811) — fresh verified 2026-10-23T11:27:13.928Z; [receipt summary](verification-correlation.json); [58-test report](correlation-direct-tests.xml).
- [cardinality workflow](https://github.com/moorisi/repair-scope/actions/runs/39945035609) — fresh verified 2026-10-23T11:26:24.026Z; [receipt summary](verification-cardinality.json); [58-test report](cardinality-direct-tests.xml).
- [unresolved workflow](https://github.com/moorisi/repair-scope/actions/runs/39945043643) — fresh verified 2026-10-23T11:27:28.486Z; [receipt summary](verification-unresolved.json); [58-test report](unresolved-direct-tests.xml).

All three hosted XML reports contain 58 passes and zero failures, errors or skips. Local lint, 58 direct tests and seven transport tests passed. Independent oracles cover all 256 two-by-two-by-two databases, 96 generated larger databases, correlated three-atom joins, duplicate/reordering invariance, validator disagreements, omitted/unknown decisions, malformed sources and model output, constructor limits, rollback, and view access after the sixteen-entry query journal fills.

The earlier [correlation](https://github.com/moorisi/repair-scope/actions/runs/39944803856), [cardinality](https://github.com/moorisi/repair-scope/actions/runs/39944824328) and [unresolved](https://github.com/moorisi/repair-scope/actions/runs/39944839441) workflow attempts on `cd5b2541577049359369fb6ccb76497ba6c9d5fa` were cancelled when unrestricted evaluation was added. They are excluded from this final-source proof set.

## Reproduce

Install the locked tooling with `npm ci`, set `GENLAYER_CLI_PATH` to the installed `node_modules/genlayer/dist/index.js`, and run `node scripts/verify-proofs.cjs --offline`. With a configured StudioNet CLI account, omit `--offline` for fresh read-only RPC verification. Neither verifier submits transactions. The workflow_dispatch scenario jobs perform deployments separately.

## Scope

Synthetic reports demonstrate the mechanism, not physical custody or publisher honesty. C-repair semantics explicitly prefer the most retained distinct tuples; excluded assertions are not proven false. Repair frequencies are not probabilities. UNKNOWN blocks the whole snapshot. A stranger can fill the bounded public query journal, but cannot block the read-only evaluate method. Sources and policies are immutable; corrections require a new deployment. Proof callers are disposable encrypted CI accounts; the oracle needs no privileged signing key after compilation. This is StudioNet, not a mainnet deployment.
