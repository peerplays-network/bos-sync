import json
import os
import mock
import unittest
import datetime
from pprint import pprint
from peerplays import PeerPlays
from peerplays.event import Event
from peerplays.rule import Rules
from peerplays.eventgroup import EventGroups
from peerplays.bettingmarket import BettingMarkets
from peerplays.bettingmarketgroup import BettingMarketGroups
from peerplays.blockchainobject import BlockchainObject, ObjectCache
from peerplays.instance import set_shared_blockchain_instance
from bookied_sync.lookup import Lookup
from bookied_sync.eventgroup import LookupEventGroup
from bookied_sync.event import LookupEvent
from bookied_sync.bettingmarketgroupresolve import (
    LookupBettingMarketGroupResolve
)
from bookied_sync.rule import LookupRules

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
test_result = [2, 3]
test_operation_dicts = [
    {
        "id": this_id,
        "betting_market_group_id": "AFG",
        "resolutions": [
            ["1.21.257", "win"],
            ["1.21.258", "not_win"],
            ["1.21.259", "cancel"],
        ],
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
            ['grading', json.dumps({
                'metric': '{result.hometeam} - {result.awayteam}',
                'resolutions': [{'win': '{metric} > 0',
                                 'not_win': '{metric} <= 0',
                                 'void': 'False'},
                                {'win': '{metric} < 0',
                                 'not_win': '{metric} >= 0',
                                 'void': 'False'},
                                {'win': '{metric} == 0',
                                 'not_win': '{metric} != 0',
                                 'void': 'False'}]})]
        ]}
]

additional_objects["bms"] = [
    {"id": "1.21.257",
     "description": [["en", "Demo wins"]], "group_id": "1.18.0"},
    {"id": "1.21.258",
     "description": [["en", "Foobar wins"]], "group_id": "1.18.0"},
    {"id": "1.21.259",
     "description": [["en", "Draw"]], "group_id": "1.18.0"},
]
wif = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"

ppy = PeerPlays(
    nobroadcast=True,
    wif=[wif]   # ensure we can sign
)
set_shared_blockchain_instance(ppy)
mock_resolutions = (
    "bookied_sync.bettingmarketgroupresolve."
    "LookupBettingMarketGroupResolve.resolutions"
)


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

        self.event = LookupEvent(**miniumum_event_dict)
        self.bmg = next(self.event.bettingmarketgroups)
        # overwrite the BMG id since we cannot look on the chain
        self.bmg["id"] = "1.20.0"

        self.lookup = LookupBettingMarketGroupResolve(
            self.bmg, test_result
        )

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

        Rules.cache["rules"] = additional_objects["rules"]
        BettingMarkets.cache[parent_id] = additional_objects["bms"]

    def test_init(self):
        self.assertIsInstance(self.lookup, LookupBettingMarketGroupResolve)

    def test_sport(self):
        self.assertEqual(
            self.lookup.sport["identifier"],
            self.event.sport["identifier"])

    def test_rules(self):
        self.assertIsInstance(self.lookup.rules, LookupRules)

    def test_test_operation_equal(self):
        def mock_result(*args, **kwargs):
            return test_operation_dicts[0]["resolutions"]

        with mock.patch(
            "bookied_sync.bettingmarketgroupresolve." +
            "LookupBettingMarketGroupResolve.resolutions",
            new_callable=mock_result
        ):
            for x in test_operation_dicts:
                self.assertTrue(self.lookup.test_operation_equal(x))

    def test_find_id(self):
        pass

    def test_is_synced(self):
        """ FIXME: We always return False because the blockchain doesn't tell
            us yet if the bmgs have already been resolved.

        """
        return False

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
        pass

    def test_resolution(self):
        # Away Team wins
        lookup = LookupBettingMarketGroupResolve(
            self.bmg, [2, 3]
        )
        res = lookup.resolutions
        # should be:
        #    [['1.21.257', 'not_win'],
        #     ['1.21.258', 'win'],
        #     ['1.21.259', 'not_win']]
        self.assertEqual(res[0][1], "not_win")
        self.assertEqual(res[1][1], "win")
        self.assertEqual(res[2][1], "not_win")

        # Draw
        lookup = LookupBettingMarketGroupResolve(
            self.bmg, [3, 3]
        )
        res = lookup.resolutions
        # should be:
        #    [['1.21.257', 'not_win'],
        #     ['1.21.258', 'not_win'],
        #     ['1.21.259', 'win']]
        self.assertEqual(res[0][1], "not_win")
        self.assertEqual(res[1][1], "not_win")
        self.assertEqual(res[2][1], "win")

        # Home Team wins
        lookup = LookupBettingMarketGroupResolve(
            self.bmg, [4, 3]
        )
        res = lookup.resolutions
        # should be:
        #    [['1.21.257', 'win'],
        #     ['1.21.258', 'not_win'],
        #     ['1.21.259', 'not_win']]
        self.assertEqual(res[0][1], "win")
        self.assertEqual(res[1][1], "not_win")
        self.assertEqual(res[2][1], "not_win")
