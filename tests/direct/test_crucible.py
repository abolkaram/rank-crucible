from conftest import CONTRACT
import json


OPTIONS = ['North Hall', 'River Annex', 'Workshop Court']
TEXTS = [
    'My complete order is North Hall first, River Annex second, and Workshop Court third.',
    'I rank North Hall first, Workshop Court second, and River Annex third.',
    'My preference is River Annex first, then North Hall, then Workshop Court.',
]


def opened(vm, deploy, accounts, window=600, count=3):
    vm.strict_mocks = True; vm.check_pickling = True; vm.warp('2035-01-01T00:00:00+00:00'); vm.sender = accounts[0]
    contract = deploy(CONTRACT)
    contract.open_ballot('vote-8', 'Shared workshop location', OPTIONS, ['0x' + a.hex() for a in accounts[1:count + 1]], window)
    return contract


def submit(vm, contract, accounts, indexes=(1, 2, 3)):
    for account_index, text in zip(indexes, TEXTS):
        vm.sender = accounts[account_index]; contract.submit_statement('vote-8', text)


def llm(vm, rankings=None):
    rankings = rankings or [[0, 1, 2], [0, 2, 1], [1, 0, 2]]
    vm.mock_llm(r'.*RankCrucible preference normalization.*', json.dumps({'rows': [
        {'index': index, 'ranking': ranking} for index, ranking in enumerate(rankings)
    ]}))


def test_unique_condorcet_winner(direct_vm, direct_deploy, direct_accounts):
    contract = opened(direct_vm, direct_deploy, direct_accounts); submit(direct_vm, contract, direct_accounts); llm(direct_vm)
    contract.tally_ballot('vote-8'); row = contract.get_ballot('vote-8')
    assert row['state'] == 'DECIDED' and row['winner_index'] == 0 and row['winner_label'] == 'North Hall'
    assert row['matrix'][0][1] == 2 and row['matrix'][0][2] == 3


def test_pairwise_cycle_is_preserved(direct_vm, direct_deploy, direct_accounts):
    contract = opened(direct_vm, direct_deploy, direct_accounts); submit(direct_vm, contract, direct_accounts)
    llm(direct_vm, [[0, 1, 2], [1, 2, 0], [2, 0, 1]]); contract.tally_ballot('vote-8')
    row = contract.get_ballot('vote-8'); assert row['state'] == 'CYCLE' and row['winner_label'] == ''


def test_named_voter_and_replay(direct_vm, direct_deploy, direct_accounts):
    contract = opened(direct_vm, direct_deploy, direct_accounts); direct_vm.sender = direct_accounts[4]
    with direct_vm.expect_revert('named voter'):
        contract.submit_statement('vote-8', TEXTS[0])
    direct_vm.sender = direct_accounts[1]; contract.submit_statement('vote-8', TEXTS[0])
    with direct_vm.expect_revert('one statement'):
        contract.submit_statement('vote-8', TEXTS[0])


def test_sparse_expired_ballot_uses_dense_indexes(direct_vm, direct_deploy, direct_accounts):
    contract = opened(direct_vm, direct_deploy, direct_accounts, 30, 4); submit(direct_vm, contract, direct_accounts, (1, 3, 4))
    direct_vm.warp('2035-01-01T00:00:31+00:00'); llm(direct_vm); contract.tally_ballot('vote-8')
    assert contract.get_ballot('vote-8')['state'] == 'DECIDED'


def test_validator_rejects_forged_ranking(direct_vm, direct_deploy, direct_accounts):
    contract = opened(direct_vm, direct_deploy, direct_accounts); submit(direct_vm, contract, direct_accounts); llm(direct_vm)
    texts = [{'index': i, 'voter_index': i, 'text': TEXTS[i]} for i in range(3)]
    result = contract._normalize(contract.ballots['VOTE-8'], texts); assert direct_vm.run_validator(leader_result=result) is True
    forged = {'rows': [{'index': item['index'], 'ranking': list(item['ranking'])} for item in result['rows']]}
    forged['rows'][0]['ranking'] = [2, 1, 0]
    assert direct_vm.run_validator(leader_result=forged) is False


def test_incomplete_ranking_is_rejected(direct_vm, direct_deploy, direct_accounts):
    contract = opened(direct_vm, direct_deploy, direct_accounts); submit(direct_vm, contract, direct_accounts)
    llm(direct_vm, [[0, 1], [0, 2, 1], [1, 0, 2]])
    with direct_vm.expect_revert('complete option permutation'):
        contract.tally_ballot('vote-8')


def test_permissionless_incomplete_close(direct_vm, direct_deploy, direct_accounts):
    contract = opened(direct_vm, direct_deploy, direct_accounts, 30); direct_vm.warp('2035-01-01T00:00:31+00:00'); direct_vm.sender = direct_accounts[5]
    contract.close_incomplete('vote-8'); assert contract.get_ballot('vote-8')['state'] == 'INCOMPLETE'
