import os
import mock
import unittest
import datetime
from pprint import pprint
from peerplays import PeerPlays
from peerplays.event import Event
from peerplays.rule import Rules
from peerplays.proposal import Proposals, Proposal
from peerplays.eventgroup import EventGroups
from peerplays.bettingmarketgroup import BettingMarketGroups
from peerplays.blockchainobject import BlockchainObject, ObjectCache
from peerplays.instance import set_shared_blockchain_instance
from bookied_sync.lookup import Lookup
from bookied_sync.eventgroup import LookupEventGroup
from bookied_sync.event import LookupEvent
from bookied_sync.bettingmarketgroup import LookupBettingMarketGroup
from peerplays.utils import parse_time

from .fixtures import fixture_data, config, lookup_test_eventgroup


sport_id = "1.20.1"
event_group_id = "1.21.12"

test_operation_dict = {
    "id": event_group_id,
    "name": [
        ["en", "NBA Regular Season"],
        ["identifier", "NBA Regular Season"],
        ["sen", "NBA"],
    ],
    "sport_id": sport_id,
}


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fixture_data()
        self.lookup = lookup_test_eventgroup(event_group_id)

    def test_eventgroup(self):
        self.assertIsInstance(self.lookup, dict)
        self.assertIsInstance(self.lookup.peerplays, PeerPlays)
        self.assertEqual(self.lookup["name"]["en"], "NBA Regular Season")
        self.assertTrue(self.lookup.parent)
        self.assertTrue(self.lookup.sport_id)
        self.assertEqual(self.lookup.parent_id, self.lookup.sport_id)

    def test_test_operation_equal(self):
        self.assertTrue(self.lookup.test_operation_equal(test_operation_dict))

        with self.assertRaises(ValueError):
            self.assertTrue(self.lookup.test_operation_equal({}))

    def test_find_id(self):
        self.assertEqual(self.lookup.find_id(), event_group_id)

    def test_is_synced(self):
        self.lookup["id"] = event_group_id
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

        self.lookup["id"] = event_group_id
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

    def test_approve_proposal(self):
        # We need an approver account
        self.lookup.set_approving_account("init0")

        # We need to delete id else, bos-sync will not try to create
        self.lookup["id"] = None
        self.lookup.clear_proposal_buffer()
        tx = self.lookup.propose_new()
        tx = tx.json()
        propops = tx["operations"][0][1]["proposed_ops"][0]["op"]
        Proposals._import(
            [
                Proposal(
                    {
                        "available_active_approvals": [],
                        "available_key_approvals": [],
                        "available_owner_approvals": [],
                        "expiration_time": "2018-05-17T15:20:25",
                        "id": "1.10.2413",
                        "proposed_transaction": {
                            "expiration": "2018-05-17T15:17:48",
                            "extensions": [],
                            "operations": [propops],
                            "ref_block_num": 0,
                            "ref_block_prefix": 0,
                        },
                        "proposer": "1.2.8",
                        "required_active_approvals": ["1.2.1"],
                        "required_owner_approvals": [],
                    }
                )
            ],
            "witness-account",
        )
        # import logging
        # logging.basicConfig(level=logging.DEBUG)
        pending_propos = list(self.lookup.has_pending_new(require_witness=False))
        self.assertTrue(len(pending_propos) > 0)
        self.assertIn(pending_propos[0]["pid"], self.lookup.approval_map)
        self.assertFalse(self.lookup.is_synced())
        self.assertEqual(len(pending_propos), 1)
        self.assertEqual(pending_propos[0]["pid"], "1.10.2413")
        self.lookup.approve(**pending_propos[0])
        self.assertNotIn(pending_propos[0]["pid"], self.lookup.approval_map)
