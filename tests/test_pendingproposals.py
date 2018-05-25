import os
import mock
import unittest
from peerplays import PeerPlays
from bookied_sync.lookup import Lookup
from bookied_sync.sport import LookupSport
from peerplaysbase.operationids import operations
from peerplays.blockchainobject import BlockchainObject, ObjectCache
from peerplays.instance import set_shared_blockchain_instance

this_id = "1.16.0"

test_operation_dicts = [
    {
        "id": this_id,
        "name": [["en", "American Football"], ["de", "Amerikanisches Football"], ['identifier', 'AmericanFootball']],
    }
]
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
            network="unittests",
            sports_folder=os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "bookiesports"
            ),
            peerplays_instance=ppy
        )
        self.lookup = LookupSport("AmericanFootball")
        self.setupCache()

    def setupCache(self):
        _cache = ObjectCache(default_expiration=60 * 60 * 1, no_overwrite=True)
        for i in test_operation_dicts:
            _cache[i["id"]] = i
        for _, j in additional_objects.items():
            for i in j:
                _cache[i["id"]] = i
        BlockchainObject._cache = _cache

    def setUp(self):
        self.lookup.clear_proposal_buffer()
        self.lookup.clear_direct_buffer()

    def test_search_pending_props(self):
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
