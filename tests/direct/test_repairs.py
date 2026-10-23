import ast
import copy
import hashlib
import itertools
import json
from pathlib import Path
import random
import re
import pytest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'contracts/repair_scope.py'
REPO = 'moorisi/repair-scope'
ROSTERS = {'assets': ['asset-amber', 'asset-bronze', 'asset-copper'], 'holders': ['holder-red', 'holder-blue'], 'sites': ['site-north', 'site-south']}


def functions():
    names = {'integer', 'conflict', 'repair_database', 'valid_query', 'query_witness', 'answer_query', 'valid_observations'}
    tree = ast.parse(SOURCE.read_text())
    ns = {'re': re}
    exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name in names], type_ignores=[]), str(SOURCE), 'exec'), ns)
    return ns


F = functions()


def record(case='correlation'):
    raw = (ROOT / 'fixtures' / (case + '.json')).read_bytes()
    return f'https://raw.githubusercontent.com/{REPO}/' + 'a' * 40 + f'/fixtures/{case}.json', hashlib.sha256(raw).hexdigest(), raw


def answer(case='correlation'):
    source = json.loads(record(case)[2])
    rows = json.loads((ROOT / 'tests' / (case + '-expected.json')).read_text())
    return {'rows': [dict(row, quote=source['records'][i]['text']) for i, row in enumerate(rows)]}


def deploy(factory, case='correlation', body=None, **kwargs):
    url, sha, raw = record(case)
    args = dict(repository=REPO, snapshot=case + '-snapshot', **ROSTERS,
                records=[r['id'] for r in json.loads(raw)['records']], url=url,
                sha256=hashlib.sha256(body).hexdigest() if body is not None else sha)
    args.update(kwargs)
    return factory(str(SOURCE), **args)


def mocks(vm, case='correlation', proposed=None, audit=None, body=None, status=200):
    vm.clear_mocks()
    url, _, raw = record(case)
    vm.mock_web(re.escape(url), {'status': status, 'body': raw if body is None else body})
    vm.mock_llm(r'.*REPAIRSCOPE-EXTRACT.*', json.dumps(answer(case) if proposed is None else proposed))
    vm.mock_llm(r'.*REPAIRSCOPE-AUDIT.*', json.dumps({'rows': [True] * len(answer(case)['rows'])} if audit is None else audit))


def compile_snapshot(c, vm, case='correlation'):
    mocks(vm, case)
    c.compile()
    assert vm.run_validator() is True


def rows_for(facts):
    return [dict(id='record-' + str(i), status='ASSERTED', asset=a, holder=h, site=s) for i, (a, h, s) in enumerate(facts)]


def independent_repairs(facts):
    # Independent enumeration by asset choices, not contract bit masks/conflict edges.
    facts = sorted(set(map(tuple, facts)))
    assets = sorted({x[0] for x in facts})
    candidates = []
    for choices in itertools.product(*[[None] + [f for f in facts if f[0] == a] for a in assets]):
        selected = [f for f in choices if f is not None]
        locations = {}
        for _, holder, site in selected:
            locations.setdefault(holder, set()).add(site)
        if all(len(values) == 1 for values in locations.values()):
            candidates.append(sorted(facts.index(f) for f in selected))
    maximum = max(map(len, candidates))
    return maximum, sorted(x for x in candidates if len(x) == maximum)


def independent_query(atoms, facts, repair):
    # Cartesian products of complete atom assignments; no recursive join algorithm.
    for assignment in itertools.product(repair, repeat=len(atoms)):
        bindings = {}
        valid = True
        for atom, index in zip(atoms, assignment):
            for term, value in zip(atom, facts[index]):
                if term.startswith('?'):
                    if term in bindings and bindings[term] != value: valid = False
                    bindings[term] = value
                elif term != value: valid = False
        if valid: return {'facts': list(assignment), 'bindings': bindings}
    return None


QUERIES = [
    [['asset-amber', '?h', 'site-north']],
    [['asset-amber', '?h', 'site-north'], ['asset-bronze', '?h', 'site-north']],
    [['?a', '?h', 'site-south']],
]


@pytest.mark.parametrize('case,expected', [('correlation', ['CERTAIN', 'POSSIBLE', 'IMPOSSIBLE']), ('cardinality', ['IMPOSSIBLE', 'CERTAIN', 'CERTAIN'])])
def test_full_permissionless_query_flow(direct_deploy, direct_vm, direct_accounts, case, expected):
    c = deploy(direct_deploy, case)
    before = c.get_state()
    with direct_vm.expect_revert('Snapshot not compiled'): c.query(QUERIES[0])
    assert c.get_state() == before
    direct_vm.sender = direct_accounts[3]
    compile_snapshot(c, direct_vm, case)
    queries = QUERIES if case == 'correlation' else [
        [['asset-amber', 'holder-red', '?s']],
        [['asset-bronze', 'holder-red', 'site-north'], ['asset-copper', 'holder-red', 'site-north']],
        QUERIES[2]]
    for i, query in enumerate(queries):
        direct_vm.sender = direct_accounts[i + 1]
        c.query(query)
    state = c.get_state()
    assert [a['status'] for a in state['answers']] == expected
    maximum, repairs = independent_repairs(state['database']['facts'])
    assert (state['database']['maximum_size'], state['database']['repairs']) == (maximum, repairs)
    with direct_vm.expect_revert('Snapshot already compiled'): c.compile()
    assert c.get_state() == state


def test_certain_query_without_any_certain_fact(direct_deploy, direct_vm):
    c = deploy(direct_deploy); compile_snapshot(c, direct_vm)
    assert c.get_state()['database']['certain_facts'] == []
    assert len(c.get_state()['database']['repairs']) == 4
    c.query(QUERIES[0])
    result = c.get_state()['answers'][0]
    assert result['status'] == 'CERTAIN' and result['true_repairs'] == [0, 1, 2, 3]


def test_duplicates_do_not_vote_and_maximal_is_not_maximum(direct_deploy, direct_vm):
    c = deploy(direct_deploy, 'cardinality'); compile_snapshot(c, direct_vm, 'cardinality')
    db = c.get_state()['database']
    assert len(db['facts']) == 4 and db['maximum_size'] == 3 and len(db['repairs']) == 1
    duplicate = db['facts'].index(['asset-bronze', 'holder-red', 'site-north'])
    assert db['origins'][duplicate] == ['record-2', 'record-5']
    assert all('record-6' not in xs and 'record-7' not in xs for xs in db['origins'])
    smaller = db['facts'].index(['asset-amber', 'holder-red', 'site-south'])
    assert all(F['conflict'](db['facts'][smaller], fact) for i, fact in enumerate(db['facts']) if i != smaller)
    assert smaller not in db['repairs'][0]  # singleton is maximal, but not maximum.


def test_unknown_blocks_every_query_without_deleting_record(direct_deploy, direct_vm):
    c = deploy(direct_deploy, 'unresolved'); compile_snapshot(c, direct_vm, 'unresolved')
    before = c.get_state()
    assert before['database']['status'] == 'REVIEW'
    assert before['database']['unknown'] == ['record-3']
    assert before['database']['repairs'] == [] and before['database']['maximum_size'] == -1
    for query in QUERIES:
        with direct_vm.expect_revert('Snapshot requires review'): c.query(query)
        assert c.get_state() == before


def test_empty_known_database_has_one_empty_repair():
    db = F['repair_database']([])
    assert db['maximum_size'] == 0 and db['repairs'] == [[]]
    result = F['answer_query'](db, QUERIES[0])
    assert result['status'] == 'IMPOSSIBLE' and result['counterexample'] == 0 and result['witness'] is None


def test_exhaustive_all_256_two_by_two_by_two_databases():
    universe = list(itertools.product(['asset-amber', 'asset-bronze'], ['holder-red', 'holder-blue'], ['site-north', 'site-south']))
    for mask in range(256):
        facts = [f for i, f in enumerate(universe) if mask & (1 << i)]
        db = F['repair_database'](rows_for(facts))
        maximum, repairs = independent_repairs(facts)
        assert (db['maximum_size'], db['repairs']) == (maximum, repairs)
        assert db['certain_facts'] == [i for i in range(len(db['facts'])) if all(i in r for r in repairs)]
        for atoms in QUERIES:
            result = F['answer_query'](db, atoms)
            truth = [i for i, repair in enumerate(repairs) if independent_query(atoms, db['facts'], repair) is not None]
            assert result['true_repairs'] == truth
            assert result['status'] == ('CERTAIN' if len(truth) == len(repairs) else 'POSSIBLE' if truth else 'IMPOSSIBLE')
            if truth:
                assert result['witness'] == {'repair': truth[0], 'assignment': independent_query(atoms, db['facts'], repairs[truth[0]])}
            assert result['counterexample'] == next((i for i in range(len(repairs)) if i not in truth), None)


def test_96_generated_larger_databases_and_three_atom_joins():
    rng = random.Random(418)
    universe = list(itertools.product(ROSTERS['assets'], ROSTERS['holders'], ROSTERS['sites']))
    atoms = [['asset-amber', '?h', '?s'], ['asset-bronze', '?h', '?s'], ['asset-copper', '?h', '?s']]
    for _ in range(96):
        facts = rng.sample(universe, rng.randrange(1, 11))
        db = F['repair_database'](rows_for(facts))
        maximum, repairs = independent_repairs(facts)
        assert (db['maximum_size'], db['repairs']) == (maximum, repairs)
        expected = [i for i, repair in enumerate(repairs) if independent_query(atoms, db['facts'], repair) is not None]
        assert F['answer_query'](db, atoms)['true_repairs'] == expected


def test_reordering_and_duplicate_invariance():
    rows = answer()['rows']
    base = F['repair_database'](rows)
    for permutation in itertools.permutations(rows):
        db = F['repair_database'](list(permutation) + [rows[0]] * 4)
        for key in ['facts', 'maximum_size', 'repairs', 'certain_facts']:
            assert db[key] == base[key]


@pytest.mark.parametrize('field,value', [('status', 'OMIT'), ('status', 'UNKNOWN'), ('holder', 'holder-blue'), ('site', 'site-south'), ('asset', 'asset-copper')])
def test_validator_independently_checks_every_consequential_field(direct_deploy, direct_vm, field, value):
    c = deploy(direct_deploy); compile_snapshot(c, direct_vm)
    changed = answer(); changed['rows'][0][field] = value
    if field == 'status':
        for key in ['asset', 'holder', 'site']: changed['rows'][0][key] = ''
    mocks(direct_vm, proposed=changed)
    assert direct_vm.run_validator() is False


@pytest.mark.parametrize('case', ['cardinality', 'unresolved'])
def test_negative_omit_unknown_decisions_are_independently_checked(direct_deploy, direct_vm, case):
    c = deploy(direct_deploy, case); compile_snapshot(c, direct_vm, case)
    changed = answer(case); row = changed['rows'][-1]
    row.update(status='ASSERTED', asset='asset-copper', holder='holder-red', site='site-north')
    mocks(direct_vm, case, proposed=changed)
    assert direct_vm.run_validator() is False


@pytest.mark.parametrize('audit', [{'rows': [False, True, True, True]}, {'rows': [True]}, {'rows': [1] * 4}, {'rows': [True] * 4, 'extra': True}])
def test_full_source_substantive_audit_required(direct_deploy, direct_vm, audit):
    c = deploy(direct_deploy); compile_snapshot(c, direct_vm)
    mocks(direct_vm, audit=audit)
    assert direct_vm.run_validator() is False


def test_validator_refetches_exact_full_source(direct_deploy, direct_vm):
    c = deploy(direct_deploy); compile_snapshot(c, direct_vm)
    mocks(direct_vm, body=b'{}')
    assert direct_vm.run_validator() is False


@pytest.mark.parametrize('change', ['missing', 'reordered', 'invented-quote', 'unknown-id', 'null', 'bool', 'extra', 'wrong-quote'])
def test_bad_model_output_rolls_back(direct_deploy, direct_vm, change):
    c = deploy(direct_deploy); proposed = answer()
    row = proposed['rows'][0]
    if change == 'missing': proposed['rows'].pop()
    elif change == 'reordered': proposed['rows'].reverse()
    elif change == 'invented-quote': row['quote'] = 'A fabricated passage that is nowhere in this record.'
    elif change == 'unknown-id': row['holder'] = 'holder-green'
    elif change == 'null': row['asset'] = None
    elif change == 'bool': row['status'] = True
    elif change == 'extra': row['confidence'] = 1
    else: row['quote'] = proposed['rows'][1]['quote']
    mocks(direct_vm, proposed=proposed); before = c.get_state()
    with direct_vm.expect_revert('Invalid complete observations'): c.compile()
    assert c.get_state() == before


@pytest.mark.parametrize('change', ['scope', 'roster', 'missing', 'schema', 'duplicate', 'utf8', 'invalid-json', 'oversized'])
def test_committed_malformed_report_rejected(direct_deploy, direct_vm, change):
    source = json.loads(record()[2])
    if change == 'scope': source['snapshot'] = 'other'
    elif change == 'roster': source['records'][0]['id'] = 'record-99'
    elif change == 'missing': source['records'].pop()
    elif change == 'schema': source['records'][0]['extra'] = 'x'
    elif change == 'oversized': source['records'][0]['text'] = 'x' * 17000
    raw = json.dumps(source).encode()
    if change == 'duplicate': raw = b'{"snapshot":"one","snapshot":"two"}'
    elif change == 'utf8': raw = b'\xff'
    elif change == 'invalid-json': raw = b'{'
    c = deploy(direct_deploy, body=raw); mocks(direct_vm, body=raw)
    before = c.get_state()
    with direct_vm.expect_revert('[EXTERNAL]'): c.compile()
    assert c.get_state() == before


@pytest.mark.parametrize('status', [404, 500])
def test_web_failure_and_error_callback(direct_deploy, direct_vm, status):
    c = deploy(direct_deploy); compile_snapshot(c, direct_vm)
    mocks(direct_vm, status=status)
    message = '[EXTERNAL] Report commitment mismatch' if status == 404 else '[TRANSIENT] Report unavailable'
    assert direct_vm.run_validator(leader_error=Exception(message)) is True
    assert direct_vm.run_validator() is False


def test_llm_error_never_agrees(direct_deploy, direct_vm):
    c = deploy(direct_deploy); compile_snapshot(c, direct_vm)
    mocks(direct_vm, proposed={})
    assert direct_vm.run_validator(leader_error=Exception('[LLM_ERROR] Invalid complete observations')) is False


@pytest.mark.parametrize('atoms', [[], [[]], [['asset-amber', 'holder-red']], [['asset-amber', True, 'site-north']], [['asset-amber', 'holder-green', 'site-north']], [['?x', '?x', 'site-north']], [['?TOOLONGNAME', 'holder-red', 'site-north']], QUERIES[0] * 4])
def test_invalid_queries_rejected_without_state_change(direct_deploy, direct_vm, atoms):
    c = deploy(direct_deploy); compile_snapshot(c, direct_vm)
    before = c.get_state()
    with direct_vm.expect_revert('Invalid bounded conjunctive query'): c.query(atoms)
    assert c.get_state() == before


def test_query_capacity_and_repeat_semantics(direct_deploy, direct_vm):
    c = deploy(direct_deploy); compile_snapshot(c, direct_vm)
    for _ in range(16): c.query(QUERIES[0])
    before = c.get_state()
    assert len(before['answers']) == 16 and all(a == before['answers'][0] for a in before['answers'])
    with direct_vm.expect_revert('Query capacity reached'): c.query(QUERIES[0])
    assert c.get_state() == before
    assert c.evaluate(QUERIES[0]) == before['answers'][0]
    assert c.evaluate(QUERIES[2])['status'] == 'IMPOSSIBLE'
    assert c.get_state() == before


@pytest.mark.parametrize('kwargs', [
    {'snapshot': '../bad'}, {'repository': '../bad'}, {'records': []},
    {'records': ['record-1', 'record-1']}, {'assets': ['holder-red']},
    {'url': 'https://example.com/report'}, {'url': 'https://raw.githubusercontent.com/moorisi/repair-scope/main/fixtures/correlation.json'},
    {'sha256': 'f' * 63}, {'holders': ['Holder']},
])
def test_constructor_bounds(direct_deploy, direct_vm, kwargs):
    with direct_vm.expect_revert('[EXPECTED]'): deploy(direct_deploy, **kwargs)
