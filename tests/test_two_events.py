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

from .fixtures import fixture_data, config, lookup_test_event

event_group_id = "1.17.12"
event_id = "1.18.2242"

start_time = parse_time("2018-05-30T02:05:00")

test_operation_dict = {
    "id": event_id,
    "name": [
        ['en', 'Boston Celtics @ Atlanta Hawks']
    ],
    "event_group_id": event_group_id,
    "season": [["en", "2017"]],
    "status": "upcoming",
    "start_time": "2022-10-16T00:00:00"
}


class Testcases(unittest.TestCase):

    def setUp(self):
        fixture_data()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fixture_data()
        self.lookup = lookup_test_event(event_id)

    def test_test_operation_equal(self):
        self.assertTrue(self.lookup.test_operation_equal(test_operation_dict))

        # The second event is identical but has a different start_time
        t = test_operation_dict.copy()
        t["start_time"] = parse_time("2018-05-31T02:05:00")
        self.assertFalse(self.lookup.test_operation_equal(t))

        """
        # The second event is identical but has a different season
        t = test_operation_dict.copy()
        t["season"] = [["en", "2018"]]
        self.assertFalse(self.lookup.test_operation_equal(t))
        """

        # The second event is identical but has a different event group
        t = test_operation_dict.copy()
        t["event_group_id"] = "1.17.17"
        self.assertFalse(self.lookup.test_operation_equal(t))

        # The second event is identical but has a different event group
        t = test_operation_dict.copy()
        t["event_group_id"] = "1.17.17"
        self.assertFalse(self.lookup.test_operation_equal(t))

        # The second event is identical but has different teams
        t = test_operation_dict.copy()
        t["name"] = [["en", "Demo2 : Foobar"], ['en_us', 'Foobar @ Demo2']]
        self.assertFalse(self.lookup.test_operation_equal(t))
