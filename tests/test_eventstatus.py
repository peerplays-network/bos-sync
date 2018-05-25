import os
import mock
import unittest
import datetime
from mock import MagicMock, PropertyMock
from pprint import pprint
from peerplays import PeerPlays
from peerplays.event import Event, Events
from peerplays.proposal import Proposals
from peerplays.rule import Rules
from peerplays.eventgroup import EventGroups
from peerplays.bettingmarketgroup import BettingMarketGroups
from peerplays.blockchainobject import BlockchainObject, ObjectCache
from peerplays.instance import set_shared_blockchain_instance
from bookied_sync.lookup import Lookup
from bookied_sync.eventgroup import LookupEventGroup
from bookied_sync.event import LookupEvent
from bookied_sync.eventstatus import LookupEventStatus
from bookied_sync.rule import LookupRules

parent_id = "1.17.16"
this_id = "1.18.0"

miniumum_event_dict = {
    "id": this_id,
    "teams": ["Demo", "Foobar"],
    "eventgroup_identifier": "NFL#PreSeas",
    "sport_identifier": "AmericanFootball",
    "season": {"en": "2017-00-00"},
    "start_time": datetime.datetime.utcnow(),
}
test_result = [2, 3]
additional_objects = dict()
wif = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"

ppy = PeerPlays(
    nobroadcast=True,
    wif=[wif]   # ensure we can sign
)
set_shared_blockchain_instance(ppy)


class Testcases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        Lookup._clear()
        Lookup(
            network="unittests",
            sports_folder=os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "bookiesports"
            ),
            peerplays_instance=ppy
        )
        self.setupCache()
        self.lookup = LookupEvent(**miniumum_event_dict)

    def setUp(self):
        self.lookup.clear_proposal_buffer()

    def setupCache(self):
        _cache = ObjectCache(default_expiration=60 * 60 * 1, no_overwrite=True)
        _cache[parent_id] = {"id": parent_id}
        _cache[this_id] = miniumum_event_dict
        for _, j in additional_objects.items():
            for i in j:
                _cache[i["id"]] = i
        BlockchainObject._cache = _cache

    def test_init(self):
        self.assertIsInstance(self.lookup, LookupEvent)

    def test_status_update(self):
        from peerplaysbase.operationids import operations
        status = LookupEventStatus(self.lookup, "in_progress", scores=["foo", "bar"])
        tx = status.propose_update()
        tx = tx.json()
        self.assertIsInstance(tx, dict)
        self.assertIn("operations", tx)
        self.assertIn("ref_block_num", tx)
        self.assertEqual(tx["operations"][0][0], 22)
        self.assertEqual(
            tx["operations"][0][1]["proposed_ops"][0]["op"][0],
            operations[status.operation_update]
        )
        self.assertEqual(
            tx["operations"][0][1]["proposed_ops"][0]["op"][1]["scores"],
            ["foo", "bar"]
        )

    def test_approve_proposal(self):
        # We need an approver account
        self.lookup.set_approving_account("init0")

        # We need to delete id else, bos-sync will not try to create
        self.lookup["id"] = None
        self.lookup.clear_proposal_buffer()
        tx = self.lookup.propose_new()
        tx = tx.json()
        propops = tx["operations"][0][1]["proposed_ops"][0]["op"]
        Proposals.cache["1.2.1"] = [{
            'available_active_approvals': [],
            'available_key_approvals': [],
            'available_owner_approvals': [],
            'expiration_time': '2018-05-17T15:20:25',
            'id': '1.10.2413',
            'proposed_transaction': {'expiration': '2018-05-17T15:17:48',
                                     'extensions': [],
                                     'operations': [propops],
                                     'ref_block_num': 0,
                                     'ref_block_prefix': 0},
            'proposer': '1.2.8',
            'required_active_approvals': ['1.2.1'],
            'required_owner_approvals': []
        }]
        # import logging
        # logging.basicConfig(level=logging.DEBUG)
        pending_propos = list(self.lookup.has_pending_new())
        self.assertIn(
            pending_propos[0]["pid"],
            self.lookup.approval_map
        )
        self.assertFalse(self.lookup.is_synced())
        self.assertEqual(len(pending_propos), 1)
        self.assertEqual(pending_propos[0]["pid"], "1.10.2413")
        self.lookup.approve(**pending_propos[0])
        self.assertNotIn(
            pending_propos[0]["pid"],
            self.lookup.approval_map
        )
