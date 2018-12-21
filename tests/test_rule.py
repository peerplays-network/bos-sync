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
from bookied_sync.rule import LookupRules
from bookied_sync.eventgroup import LookupEventGroup
from bookied_sync.event import LookupEvent
from bookied_sync.bettingmarketgroup import LookupBettingMarketGroup
from peerplays.utils import parse_time

from .fixtures import fixture_data, config, lookup_test_event

rule_id = "1.23.12"
test_operation_dicts = [
    {
        "name": [["en", "R_NBA_OU_1"], ["identifier", "R_NBA_OU_1"]],
        "id": rule_id,
        "description": [
            ["en", "Foobar"],
            [
                "grading",
                '{"metric": "{result.total}", "resolutions": [{"not_win": "{metric} > {overunder.value}", "void": "False", "win": "{metric} <= {overunder.value}"}, {"not_win": "{metric} <= {overunder.value}", "void": "False", "win": "{metric} > {overunder.value}"}]}',
            ],
        ],
    }
]


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fixture_data()
        self.lookup = LookupRules("Basketball", "R_NBA_OU_1")

    def test_test_operation_equal(self):
        for x in test_operation_dicts:
            self.assertTrue(self.lookup.test_operation_equal(x))

        with self.assertRaises(ValueError):
            self.assertTrue(self.lookup.test_operation_equal({}))

    def test_find_id(self):
        self.assertEqual(self.lookup.find_id(), rule_id)

    def test_is_synced(self):
        self.lookup["id"] = rule_id
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
            operations[self.lookup.operation_create],
        )

    def test_propose_update(self):
        from peerplaysbase.operationids import operations

        self.lookup["id"] = rule_id
        self.lookup.clear_proposal_buffer()
        tx = self.lookup.propose_update()
        tx = tx.json()
        self.assertIsInstance(tx, dict)
        self.assertIn("operations", tx)
        self.assertIn("ref_block_num", tx)
        self.assertEqual(tx["operations"][0][0], 22)
        self.assertEqual(
            tx["operations"][0][1]["proposed_ops"][0]["op"][0],
            operations[self.lookup.operation_update],
        )
