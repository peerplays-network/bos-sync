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
from peerplays.utils import parse_time, formatTime

from .fixtures import fixture_data, config, lookup_test_event

event_group_id = "1.21.12"
event_id = "1.22.2242"

start_time = parse_time(formatTime(datetime.datetime.utcnow()))
start_time_tomorrow = parse_time(formatTime(datetime.datetime.utcnow() + datetime.timedelta(days=1)))

test_operation_dict = {
    "id": event_id,
    "name": [['en', 'Boston Celtics @ Atlanta Hawks']],
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

    def test_eventgroup(self):

        self.assertIsInstance(self.lookup, dict)
        self.assertIsInstance(self.lookup.peerplays, PeerPlays)

        self.assertTrue(self.lookup.parent)
        self.assertTrue(self.lookup.event_group_id)
        self.assertEqual(self.lookup.parent_id, self.lookup.event_group_id)

    def test_eventscheme_namecreation(self):
        self.assertIn(
            test_operation_dict["name"][0],
            self.lookup.names
        )

    def test_test_operation_equal(self):
        self.assertTrue(self.lookup.test_operation_equal(test_operation_dict))

        with self.assertRaises(ValueError):
            self.assertTrue(self.lookup.test_operation_equal({}))

    def test_find_id(self):
        self.assertEqual(self.lookup.find_id(), event_id)

    def test_is_synced(self):
        self.lookup["id"] = event_id
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

        self.lookup["id"] = event_id
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

    def test_init(self):
        self.assertIsInstance(self.lookup, LookupEvent)
        self.assertIsInstance(LookupEvent(**{
            "teams": ["Atlanta Hawks", "Boston Celtics"],
            "eventgroup_identifier": "NBA",
            "sport_identifier": "Basketball",
            "season": {"en": "2017-00-00"},
            "start_time": start_time
        }), LookupEvent)

        with self.assertRaises(ValueError):
            self.assertIsInstance(LookupEvent(**{
                "teams": ["Atlanta Hawks", "Boston Celtics"],
                "eventgroup_identifier": "NBA",
                "sport_identifier": "Basketball",
                "season": {"en": "2017-00-00"},
                "start_time": "SOME STRING"
            }), LookupEvent)

        with self.assertRaises(ValueError):
            self.assertIsInstance(LookupEvent(**{
                "teams": ["Atlanta Hawks", "Boston Celtics", "third TEAM"],
                "eventgroup_identifier": "NBA",
                "sport_identifier": "Basketball",
                "season": {"en": "2017-00-00"},
                "start_time": start_time
            }), LookupEvent)

        with self.assertRaises(TypeError):
            self.assertIsInstance(LookupEvent(**{
                "eventgroup_identifier": "NBA",
                "sport_identifier": "Basketball",
                "season": {"en": "2017-00-00"},
                "start_time": start_time
            }), LookupEvent)

        with self.assertRaises(TypeError):
            self.assertIsInstance(LookupEvent(**{
                "teams": ["Atlanta Hawks", "Boston Celtics"],
                "sport_identifier": "Basketball",
                "season": {"en": "2017-00-00"},
                "start_time": start_time
            }), LookupEvent)

        with self.assertRaises(TypeError):
            self.assertIsInstance(LookupEvent(**{
                "teams": ["Atlanta Hawks", "Boston Celtics"],
                "eventgroup_identifier": "NBA",
                "season": {"en": "2017-00-00"},
                "start_time": start_time
            }), LookupEvent)

        with self.assertRaises(TypeError):
            self.assertIsInstance(LookupEvent({
                "teams": ["Atlanta Hawks", "Boston Celtics"],
                "eventgroup_identifier": "NBA",
                "sport_identifier": "Basketball",
                "start_time": start_time
            }), LookupEvent)

        self.assertIsInstance(self.lookup["teams"], list)
        self.assertEqual(self.lookup["teams"][0], "Atlanta Hawks")
        self.assertEqual(self.lookup["teams"][1], "Boston Celtics")

    def test_participants(self):
        with self.assertRaises(ValueError):
            LookupEvent(**{
                "teams": ["Atlanta Hawks", "Boston Celtics-Not"],
                "eventgroup_identifier": "NBA",
                "sport_identifier": "Basketball",
                "season": {"en": "2017-00-00"},
                "start_time": start_time
            })

        LookupEvent(**{
            "teams": ["Nets", "Mavericks"],
            "eventgroup_identifier": "NBA",
            "sport_identifier": "Basketball",
            "season": {"en": "2017-00-00"},
            "start_time": start_time
        })

    def test_leadtimemax_close(self):
        event = LookupEvent(
            sport_identifier=self.lookup["sport_identifier"],
            eventgroup_identifier=self.lookup["eventgroup_identifier"],
            teams=self.lookup["teams"],
            start_time=parse_time("2020-05-28T15:14:26")
        )

        # We set the leadtime_max to 2 days
        leadtime_Max = event.eventgroup["leadtime_Max"]

        # If the event starts now, it should be allowed to open
        event["start_time"] = datetime.datetime.utcnow()
        self.assertTrue(event.can_open)

        # If we move the start time forward to leadtime_max-1minute, it should
        # stil open
        event["start_time"] = datetime.datetime.utcnow() + datetime.timedelta(days=leadtime_Max, minutes=-1)
        self.assertTrue(event.can_open)

        # If we move it further, it should fail to open
        event["start_time"] = datetime.datetime.utcnow() + datetime.timedelta(days=leadtime_Max, minutes=1)
        self.assertFalse(event.can_open)

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
        pending_propos = list(self.lookup.has_pending_new(require_witness=False))
        self.assertTrue(len(pending_propos) > 0)
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
