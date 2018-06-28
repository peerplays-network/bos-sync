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
from bookied_sync.bettingmarketgroupresolve import (
    LookupBettingMarketGroupResolve
)
from peerplays.utils import parse_time

from .fixtures import fixture_data, config, lookup_test_event

event_id = "1.18.2242"
bmg_id = "1.20.213"
test_operation_dict = {
    "id": bmg_id,
    "description": [
        ["display_name", "HC (0:1)"],
        ["en", "Handicap (0:1)"],
        ["sen", "Handicap (0:1)"]
    ],
    "event_id": "0.0.0",
    "rules_id": "1.19.10",
    "asset_id": "1.3.0",
    "status": "ongoing",
}


class Testcases(unittest.TestCase):

    def setUp(self):
        fixture_data()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fixture_data()

        event = lookup_test_event(event_id)
        self.lookup = list(event.bettingmarketgroups)[1]
        self.lookup.set_handicaps(home=1)

    def test_init(self):
        self.assertIsInstance(self.lookup, LookupBettingMarketGroup)

    def test_set_handicap(self):
        self.assertEqual(self.lookup["handicaps"], [1, -1])

    def test_bmg_names(self):
        self.assertIn(
            ['en', 'Handicap (0:1)'],
            self.lookup.description
        )

    def test_bms_names(self):
        bms = list(self.lookup.bettingmarkets)
        names_home = bms[0].description
        names_away = bms[1].description
        self.assertIn(['en', 'Atlanta Hawks (1)'], names_home)
        #self.assertIn(['handicap', '1'], names_home)
        self.assertIn(['en', 'Boston Celtics (-1)'], names_away)
        #self.assertIn(['handicap', '-1'], names_away)

    def test_test_operation_equal(self):
        self.assertTrue(self.lookup.test_operation_equal(test_operation_dict))

        with self.assertRaises(ValueError):
            self.assertTrue(self.lookup.test_operation_equal({}))

    def test_find_id(self):
        self.assertEqual(self.lookup.find_id(), bmg_id)

    def test_is_synced(self):
        self.lookup["id"] = bmg_id
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

        self.lookup["id"] = bmg_id
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

    def assertResult(self, resolutions, *results):
        self.assertEqual(len(results), len(resolutions))
        for r in results:
            self.assertIn(r, resolutions)

    def test_result_00_on_10(self):
        resolve = LookupBettingMarketGroupResolve(
            self.lookup, [0, 0], handicaps=[1, 0]
        )
        self.assertEqual(resolve._metric, '(0 - 1) - (0 - 0)')
        self.assertEqual(resolve.metric, -1)
        self.assertResult(
            resolve.resolutions,
            ['1.21.2952', 'not_win'],
            ['1.21.2953', 'win']
        )

    def test_result_01_on_10(self):
        resolve = LookupBettingMarketGroupResolve(
            self.lookup, [0, 1], handicaps=[1, 0]
        )
        self.assertEqual(resolve._metric, '(0 - 1) - (1 - 0)')
        self.assertEqual(resolve.metric, -2)
        self.assertResult(
            resolve.resolutions,
            ['1.21.2952', 'not_win'],
            ['1.21.2953', 'win']
        )

    def test_result_10_on_10(self):
        resolve = LookupBettingMarketGroupResolve(
            self.lookup, [1, 0], handicaps=[1, 0]
        )
        self.assertEqual(resolve._metric, '(1 - 1) - (0 - 0)')
        self.assertEqual(resolve.metric, 0)
        self.assertResult(
            resolve.resolutions,
            ['1.21.2952', 'not_win'],
            ['1.21.2953', 'not_win']
        )

    def test_result_20_on_10(self):
        resolve = LookupBettingMarketGroupResolve(
            self.lookup, [2, 0], handicaps=[1, 0]
        )
        self.assertEqual(resolve._metric, '(2 - 1) - (0 - 0)')
        self.assertEqual(resolve.metric, 1)
        self.assertResult(
            resolve.resolutions,
            ['1.21.2952', 'win'],
            ['1.21.2953', 'not_win']
        )

    def test_result_00_on_20(self):
        self.lookup.set_handicaps(home=2)
        resolve = LookupBettingMarketGroupResolve(
            self.lookup, [0, 0], handicaps=[2, 0]
        )
        self.assertEqual(resolve._metric, '(0 - 2) - (0 - 0)')
        self.assertEqual(resolve.metric, -2)
        self.assertResult(
            resolve.resolutions,
            ['1.21.2954', 'not_win'],
            ['1.21.2955', 'win']
        )
