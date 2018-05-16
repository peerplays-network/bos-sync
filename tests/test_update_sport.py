import os
import mock
import unittest
from pprint import pprint
from peerplays import PeerPlays
from bookied_sync.lookup import Lookup
from bookied_sync.sport import LookupSport
from peerplays.instance import set_shared_blockchain_instance
import logging
logging.basicConfig(level=logging.INFO)

UNLOCK = "posaune"

ppy = PeerPlays(
    nobroadcast=False,
    blocking=True
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
        self.lookup = LookupSport("AmericanFootball")

    def test_update(self):
        self.lookup.blockchain.unlock(UNLOCK)
        self.lookup.set_proposing_account("init0")
        self.lookup.set_approving_account("init1")
        self.lookup.clear_proposal_buffer(1 * 60)
        self.lookup.update()
        reply = self.lookup.broadcast()
        for x in reply:
            pprint(dict(x))
        print([x.get_proposal_id() for x in reply])
