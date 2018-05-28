import os
import mock
import unittest
import datetime
from mock import MagicMock, PropertyMock
from pprint import pprint
from peerplays import PeerPlays
from peerplays.event import Event, Events
from peerplays.rule import Rules
from peerplays.proposal import Proposals
from peerplays.eventgroup import EventGroups
from peerplays.bettingmarketgroup import BettingMarketGroups
from peerplays.blockchainobject import BlockchainObject, ObjectCache
from peerplays.instance import set_shared_blockchain_instance
from bookied_sync.lookup import Lookup
from bookied_sync.eventgroup import LookupEventGroup
from bookied_sync.event import LookupEvent
from bookied_sync.bettingmarketgroup import LookupBettingMarketGroup
from peerplays.utils import parse_time
from peerplays.utils import formatTime

parent_id = "1.17.16"
this_id = "1.18.0"

start_time = parse_time("2018-05-30T02:05:00")

miniumum_event_dict = {
    "id": "1.18.0",
    "teams": ["Demo", "Foobar"],
    "eventgroup_identifier": "NFL#PreSeas",
    "sport_identifier": "AmericanFootball",
    "season": {"en": "2017-00-00"},
    "start_time": start_time,
    "status": "upcoming",
}
test_operation_dicts = [
    {
        "id": this_id,
        "name": [["en", "Demo : Foobar"], ['en_us', 'Foobar @ Demo']],
        "event_group_id": parent_id,
        "season": [["en", "2017-00-00"]],
        "start_time": start_time
    }
]
additional_objects = dict()

ppy = PeerPlays(
    nobroadcast=True,
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
        self.setupCache()
        self.lookup = LookupEvent(**miniumum_event_dict)

    def setupCache(self):
        _cache = ObjectCache(default_expiration=60 * 60 * 1, no_overwrite=True)
        _cache[parent_id] = {"id": parent_id}
        for i in test_operation_dicts:
            _cache[i["id"]] = i
        for _, j in additional_objects.items():
            for i in j:
                _cache[i["id"]] = i
        BlockchainObject._cache = _cache

    def test_test_operation_equal(self):
        self.assertTrue(self.lookup.test_operation_equal(test_operation_dicts[0]))

        # The second event is identical but has a different start_time
        t = test_operation_dicts[0].copy()
        t["start_time"] = parse_time("2018-05-31T02:05:00")
        self.assertFalse(self.lookup.test_operation_equal(t))

        """
        # The second event is identical but has a different season
        t = test_operation_dicts[0].copy()
        t["season"] = [["en", "2018"]]
        self.assertFalse(self.lookup.test_operation_equal(t))
        """

        # The second event is identical but has a different event group
        t = test_operation_dicts[0].copy()
        t["event_group_id"] = "1.17.17"
        self.assertFalse(self.lookup.test_operation_equal(t))

        # The second event is identical but has a different event group
        t = test_operation_dicts[0].copy()
        t["event_group_id"] = "1.17.17"
        self.assertFalse(self.lookup.test_operation_equal(t))

        # The second event is identical but has different teams
        t = test_operation_dicts[0].copy()
        t["name"] = [["en", "Demo2 : Foobar"], ['en_us', 'Foobar @ Demo2']]
        self.assertFalse(self.lookup.test_operation_equal(t))
