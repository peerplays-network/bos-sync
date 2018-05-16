import os
import mock
import unittest
import datetime
from peerplays import PeerPlays
from peerplays.event import Event
from peerplays.eventgroup import EventGroups
from peerplays.bettingmarket import BettingMarket, BettingMarkets
from peerplays.blockchainobject import BlockchainObject, ObjectCache
from peerplays.instance import set_shared_blockchain_instance
from bookied_sync.lookup import Lookup
from bookied_sync.eventgroup import LookupEventGroup
from bookied_sync.event import LookupEvent
from bookied_sync.bettingmarket import LookupBettingMarket
from peerplays.utils import parse_time


parent_id = "1.20.0"
this_id = "1.21.0"
miniumum_event_dict = {
    "id": "1.18.0",
    "teams": ["Demo", "Foobar"],
    "eventgroup_identifier": "NFL#PreSeas",
    "sport_identifier": "AmericanFootball",
    "season": {"en": "2017-00-00"},
    "start_time": datetime.datetime.utcnow(),
    "status": "ongoing",
}
test_operation_dicts = [
    {
        "id": this_id,
        "description": [["en", "Demo wins"]],
        "group_id": parent_id,
    }
]
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
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "testsports"
            ),
            peerplays_instance=ppy
        )

        self.setupCache()

        event = LookupEvent(**miniumum_event_dict)
        bmg = next(event.bettingmarketgroups)
        # overwrite the BMG id since we cannot look on the chain
        bmg["id"] = parent_id
        self.lookup = next(bmg.bettingmarkets)

    def setupCache(self):
        _cache = ObjectCache(default_expiration=60 * 60 * 1, no_overwrite=True)
        _cache[parent_id] = {"id": parent_id}
        _cache[miniumum_event_dict["id"]] = miniumum_event_dict
        for i in test_operation_dicts:
            _cache[i["id"]] = i
        BlockchainObject._cache = _cache

        BettingMarkets.cache[parent_id] = test_operation_dicts

    def test_init(self):
        self.assertIsInstance(self.lookup, LookupBettingMarket)

    def test_test_operation_equal(self):
        for x in test_operation_dicts:
            self.assertTrue(self.lookup.test_operation_equal(x))

        with self.assertRaises(ValueError):
            self.assertTrue(self.lookup.test_operation_equal({}))

    def test_find_id(self):
        self.assertEqual(self.lookup.find_id(), this_id)

    def test_is_synced(self):
        self.lookup["id"] = this_id
        self.assertTrue(self.lookup.is_synced())

    def test_propose_new(self):
        from peerplaysbase.operationids import operations
        self.lookup.clear_proposal_buffer()
        tx = self.lookup.propose_new()
        tx = tx.json()
        self.assertIsInstance(tx, dict)
        self.assertIn("operations", tx)
        self.assertIn("ref_block_num", tx)
        self.assertEqual(tx["operations"][0][0], 22)
        self.assertEqual(
            tx["operations"][0][1]["proposed_ops"][0]["op"][0],
            operations[self.lookup.operation_create]
        )

    def test_propose_update(self):
        from peerplaysbase.operationids import operations

        self.lookup["id"] = this_id
        self.lookup.clear_proposal_buffer()
        tx = self.lookup.propose_update()
        tx = tx.json()
        self.assertIsInstance(tx, dict)
        self.assertIn("operations", tx)
        self.assertIn("ref_block_num", tx)
        self.assertEqual(tx["operations"][0][0], 22)
        self.assertEqual(
            tx["operations"][0][1]["proposed_ops"][0]["op"][0],
            operations[self.lookup.operation_update]
        )
