import os
import mock
import unittest
import datetime
from pprint import pprint
from peerplays import PeerPlays
from peerplays.event import Event
from peerplays.rule import Rules
from peerplays.eventgroup import EventGroups
from peerplays.bettingmarketgroup import BettingMarketGroups
from peerplays.blockchainobject import BlockchainObject, ObjectCache
from peerplays.instance import set_shared_blockchain_instance
from bookied_sync.lookup import Lookup
from bookied_sync.eventgroup import LookupEventGroup
from bookied_sync.event import LookupEvent
from bookied_sync.bettingmarketgroup import LookupBettingMarketGroup
from peerplays.utils import parse_time


parent_id = "1.18.0"
this_id = "1.20.0"
miniumum_event_dict = {
    "id": parent_id,
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
        "description": [["en", "Match Odds"],
                        ["de", "Gewinn Verhältnis"],
                        ["display_name", "Match Odds"]],
        "event_id": "0.0.0",
        "rules_id": "1.19.0",
        "asset_id": "1.3.0",
        "status": "ongoing",
    }
]
additional_objects = dict()
additional_objects["rules"] = [
    {
     'name': [
         ['en', 'R_NFL_MO_1'],
     ],
     'id': '1.19.0',
     'description': [
         ['en', 'R_NFL_MO_1'],
         ['de', 'R_NFL_MO_1'],
         ['grading', str({
             'metric': '{result.hometeam} - {result.awayteam}',
             'resolutions': [{'win': '{metric} > 0',
                              'not_win': '{metric} <= 0',
                              'void': 'False'},
                             {'win': '{metric} < 0',
                              'not_win': '{metric} >= 0',
                              'void': 'False'},
                             {'win': '{metric} == 0',
                              'not_win': '{metric} != 0',
                              'void': 'False'}]})
         ]
     ]}
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
        event = LookupEvent(**miniumum_event_dict)
        self.lookup = next(event.bettingmarketgroups)

        self.setupCache()

    def setupCache(self):
        _cache = ObjectCache(default_expiration=60 * 60 * 1, no_overwrite=True)
        _cache[parent_id] = {"id": parent_id}
        _cache[miniumum_event_dict["id"]] = miniumum_event_dict
        for i in test_operation_dicts:
            _cache[i["id"]] = i
        for _, j in additional_objects.items():
            for i in j:
                _cache[i["id"]] = i
        BlockchainObject._cache = _cache

        BettingMarketGroups.cache[parent_id] = test_operation_dicts
        Rules.cache["rules"] = additional_objects["rules"]

    def test_init(self):
        self.assertIsInstance(self.lookup, LookupBettingMarketGroup)

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