import os
import unittest
from peerplays import PeerPlays
from bookied_sync.lookup import Lookup
from bookiesports.exceptions import SportsNotFoundError
import logging

log = logging.getLogger(__name__)


class Testcases(unittest.TestCase):
    def setUp(self):
        Lookup._clear()

    def test_sync(self):
        self.lookup = Lookup(
            network="unittests",
            sports_folder=os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "bookiesports"
            ),
            peerplays_instance=PeerPlays(nobroadcast=True),
        )
        self.assertIsInstance(self.lookup, dict)
        self.assertIsInstance(self.lookup.peerplays, PeerPlays)
        self.assertTrue(self.lookup.peerplays.nobroadcast)

        self.assertIn("sports", self.lookup.data)
        self.assertTrue(self.lookup.data["sports"])

    def test_proper_accounts(self):
        lookup = Lookup(
            network="unittests",
            sports_folder=os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "bookiesports"
            ),
            proposing_account="init0",
            approving_account="init1",
        )
        self.assertEqual(lookup.proposing_account, "init0")
        self.assertEqual(lookup.approving_account, "init1")
