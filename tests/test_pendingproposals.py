import os
import mock
import unittest
from peerplays import PeerPlays
from peerplays.proposal import Proposals
from bookied_sync.lookup import Lookup
from bookied_sync.sport import LookupSport
from peerplaysbase.operationids import operations
from peerplays.blockchainobject import BlockchainObject, ObjectCache
from peerplays.instance import set_shared_blockchain_instance

from .fixtures import fixture_data, config, lookup_test_event

import logging
# logging.basicConfig(level=logging.INFO)


class Testcases(unittest.TestCase):

    def setUp(self):
        self.lookup.clear_proposal_buffer()
        self.lookup.clear_direct_buffer()
        fixture_data()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fixture_data()
        self.lookup = LookupSport("AmericanFootball")
        self.lookup.set_approving_account("init0")

    def test_search_pending_props(self):
        # As defined in bookiesports
        self.assertEqual(self.lookup.id, "1.16.0")

        # Proposal creation
        self.lookup.propose_new()

        props = Lookup.proposal_buffer.json()
        self.assertIsInstance(props, list)
        self.assertIsInstance(props[1], dict)
        self.assertEqual(props[0], 22)
        proposed_op = props[1]["proposed_ops"][0]["op"]
        self.assertEqual(proposed_op[0], operations[self.lookup.operation_create])

        # The id as defined in the yaml file has priority
        self.assertEqual(self.lookup.id, "1.16.0")

        # Let's remove the id from the yaml file to load from chain
        self.lookup.pop("id", None)
        self.assertEqual(self.lookup.id, "1.16.0")

        # Let's also remove the id from chain to look into proposal buffer
        def mockedClass(m, *args, **kwargs):
            return False

        with mock.patch(
            "bookied_sync.sport.LookupSport.find_id",
            new=mockedClass
        ):
            self.lookup.pop("id", None)
            self.assertEqual(self.lookup.id, "0.0.0")

    def test_approve_proposal_instead(self):
        logging.info("Creating ....")
        self.lookup.update()

        # Now lets store the stuff in an onchain proposal already
        # by caching
        ops = list()
        for x in self.lookup.get_buffered_operations():
            ops.append(x[0])
        cache = ObjectCache(default_expiration=2.5)
        cache["1.2.1"] = [{'available_active_approvals': [],
                           'available_key_approvals': [],
                           'available_owner_approvals': [],
                           'expiration_time': '2018-05-29T10:23:13',
                           'id': '1.10.336',
                           'proposed_transaction': {'expiration': '2018-05-29T10:23:13',
                                                    'extensions': [],
                                                    'operations': ops,
                                                    'ref_block_num': 0,
                                                    'ref_block_prefix': 0},
                           'proposer': '1.2.7',
                           'required_active_approvals': ['1.2.1'],
                           'required_owner_approvals': []}]
        Proposals.cache = cache

        self.lookup.update()

        # this is supposed to be an update of the proposal 1.10.336
        tx = self.lookup.direct_buffer

        self.assertEqual(tx["operations"][0][0], 23)
        self.assertEqual(
            tx["operations"][0][1]["proposal"],
            "1.10.336",
        )
        self.assertIn(
            "1.2.7",
            tx["operations"][0][1]["active_approvals_to_add"]
        )
