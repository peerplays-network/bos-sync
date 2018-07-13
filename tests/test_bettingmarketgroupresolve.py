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
from peerplays.proposal import Proposals
from bookied_sync.lookup import Lookup
from bookied_sync.eventgroup import LookupEventGroup
from bookied_sync.event import LookupEvent
from bookied_sync.bettingmarketgroupresolve import (
    LookupBettingMarketGroupResolve
)
from bookied_sync.rule import LookupRules

from .fixtures import fixture_data, config, lookup_test_event

event_id = "1.18.2242"
bmg_id = '1.20.212'
bm_id = '1.21.2950'
test_result = [2, 3]  # home, away
test_operation_dict = {
    "id": bm_id,
    "betting_market_group_id": bmg_id,
    "resolutions": [
        ["1.21.2950", "win"],      # away
        ["1.21.2951", "not_win"],  # home
    ],
}


class Testcases(unittest.TestCase):

    def setUp(self):
        fixture_data()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fixture_data()

        self.event = lookup_test_event(event_id)
        self.bmg = next(self.event.bettingmarketgroups)
        # overwrite the BMG id since we cannot look on the chain
        self.bmg["id"] = bmg_id

        self.lookup = LookupBettingMarketGroupResolve(
            self.bmg, test_result
        )

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
            return test_operation_dict["resolutions"]

        with mock.patch(
            "bookied_sync.bettingmarketgroupresolve." +
            "LookupBettingMarketGroupResolve.resolutions",
            new_callable=mock_result
        ):
            self.assertTrue(self.lookup.test_operation_equal(test_operation_dict))

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

    def test_resolution(self):
        # Away Team wins
        lookup = LookupBettingMarketGroupResolve(
            self.bmg, [2, 3]
        )
        res = lookup.resolutions
        # should be:
        #    [["1.21.2950", "win"],
        #     ["1.21.2951", "not_win"]]
        #
        self.assertNotEqual(res[0][0], res[1][0])
        self.assertEqual(res[0], ["1.21.2950", "win"])
        self.assertEqual(res[1], ["1.21.2951", "not_win"])

        # Draw
        lookup = LookupBettingMarketGroupResolve(
            self.bmg, [3, 3]
        )
        res = lookup.resolutions
        # should be:
        #    [["1.21.2950", "not_win"],
        #     ["1.21.2951", "not_win"]]
        #
        self.assertNotEqual(res[0][0], res[1][0])
        self.assertEqual(res[0], ["1.21.2950", "not_win"])
        self.assertEqual(res[1], ["1.21.2951", "not_win"])

        # Home Team wins
        lookup = LookupBettingMarketGroupResolve(
            self.bmg, [4, 3]
        )
        res = lookup.resolutions
        # should be:
        #    [["1.21.2950", "not_win"],
        #     ["1.21.2951", "win"]]
        #
        self.assertNotEqual(res[0][0], res[1][0])
        self.assertEqual(res[0], ["1.21.2950", "not_win"])
        self.assertEqual(res[1], ["1.21.2951", "win"])

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
