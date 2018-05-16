import os
import mock
import unittest
import datetime
from mock import MagicMock, PropertyMock
from pprint import pprint
from peerplays import PeerPlays
from peerplays.event import Event, Events
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
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "testsports"
            ),
            peerplays_instance=ppy
        )
        self.setupCache()
        self.lookup = LookupEvent(**miniumum_event_dict)

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
