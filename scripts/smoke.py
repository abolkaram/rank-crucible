import json
import re
import time
from pathlib import Path

from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet
from genlayer_py.contracts import actions as contract_actions


def calldata_compat(method=None, args=None, kwargs=None):
    result = {}
    if method is not None:
        result['method'] = method
    if args:
        result['args'] = args
    if kwargs:
        result['kwargs'] = kwargs
    return result


contract_actions.make_calldata_object = calldata_compat
ROOT = Path(__file__).parents[1]
ENV = (ROOT.parents[3] / 'accounts.env').read_text()
DEPLOYMENT = json.loads((ROOT / 'deployment.json').read_text())
ADDRESS = DEPLOYMENT['contractAddress']


def account(number):
    key = re.search(rf'^ACCOUNT_{number}_GENLAYER_PRIVATE_KEY\s*=\s*"?([^"\r\n]+)', ENV, re.M).group(1).strip()
    return create_account(account_private_key=key)


def client(number):
    return create_client(chain=studionet, account=account(number))


def write(number, name, args):
    active = client(number); tx = active.write_contract(address=ADDRESS, function_name=name, args=args)
    print(name + '_tx=' + str(tx), flush=True)
    receipt = active.wait_for_transaction_receipt(transaction_hash=tx, wait_until='finalized', retries=180, interval=5000, full_transaction=True)
    leaders = receipt.get('consensus_data', {}).get('leader_receipt') or []
    leaders = [leaders] if isinstance(leaders, dict) else leaders
    assert receipt.get('result_name') == 'MAJORITY_AGREE'
    assert any(item.get('execution_result') == 'SUCCESS' for item in leaders)
    return str(tx)


ballot_id = 'VOTE-' + str(int(time.time()))
role_numbers = (1, 3, 4)
voters = [str(account(number).address) for number in role_numbers]
transactions = {}
transactions['open'] = write(5, 'open_ballot', [
    ballot_id, 'Shared workshop location', ['North Hall', 'River Annex', 'Workshop Court'], voters, 3600,
])
statements = [
    'My complete order is North Hall first, River Annex second, and Workshop Court third.',
    'I rank North Hall first, Workshop Court second, and River Annex third.',
    'My preference is River Annex first, then North Hall, then Workshop Court.',
]
for number, statement in zip(role_numbers, statements):
    transactions['statement' + str(number)] = write(number, 'submit_statement', [ballot_id, statement])
transactions['tally'] = write(5, 'tally_ballot', [ballot_id])
state = client(5).read_contract(address=ADDRESS, function_name='get_ballot', args=[ballot_id])
assert state['state'] == 'DECIDED'
assert state['winner_index'] == 0 and state['winner_label'] == 'North Hall'
proof = {'ballotId': ballot_id, 'transactions': transactions, 'state': state,
         'disclosure': 'The voter wallets are operator-controlled role fixtures, not independent people.'}
(ROOT / 'evidence').mkdir(exist_ok=True)
(ROOT / 'evidence' / 'live-proof.json').write_text(json.dumps(proof, indent=2) + '\n')
print(json.dumps(proof, indent=2), flush=True)
