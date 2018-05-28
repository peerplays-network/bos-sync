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

parent_id = "1.17.16"
this_id = "1.18.0"

start_time = parse_time(formatTime(datetime.datetime.utcnow()))
start_time_2 = parse_time("2020-05-28T15:14:26")

miniumum_event_dict = {
    "id": this_id,
    "teams": ["Demo", "Foobar"],
    "eventgroup_identifier": "NFL#PreSeas",
    "sport_identifier": "AmericanFootball",
    "season": {"en": "2017"},
    "start_time": start_time,
    "status": "ongoing",
}
test_operation_dicts = [
    {
        "id": this_id,
        "name": [["en", "Demo : Foobar"], ['en_us', 'Foobar @ Demo']],
        "event_group_id": parent_id,
        "season": [["en", "2017"]],
        "start_time": formatTime(start_time)
    }, {
        "id": "1.18.1",
        "name": [["en", "Demo : Foobar"], ['en_us', 'Foobar @ Demo']],
        "event_group_id": parent_id,
        "season": [["en", "2017"]],
        "start_time": formatTime(start_time_2)
    }
]
additional_objects = dict()
additional_objects["event_groups"] = [{
    'identifier': 'NFL#PreSeas',
    'name': {'en': 'NFL - Pre-Season',
             'de': 'NFL - Vorseason'},
    'aliases': ['National Football League - Pre-Season',
                'American Football - Pre-Season'],
    'id': parent_id,
    'participants': 'NFL_Teams_2017-18',
    'bettingmarketgroups': ['NFL_ML_2017-18_1'],
    'eventscheme': {'name': {'en': '{teams.home} : {teams.away}',
                             'en_us': '{teams.away} @ {teams.home}'}},
    'leadtime_Max': 2,
    'start_date': "2017/08/01",
    'finish_date': '2017/08/31',
    'sport_id': '1.16.0'}]

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
        self.setupCache()
        self.lookup = LookupEvent(**miniumum_event_dict)

    def setupCache(self):
        _cache = ObjectCache(default_expiration=60 * 60 * 1, no_overwrite=True)
        _cache[parent_id] = {"id": parent_id}
        #_cache[test_operation_dicts["id"]] = test_operation_dicts
        for i in test_operation_dicts:
            _cache[i["id"]] = i
        for _, j in additional_objects.items():
            for i in j:
                _cache[i["id"]] = i
        BlockchainObject._cache = _cache
        EventGroups.cache[parent_id] = additional_objects["event_groups"]
        Events.cache[parent_id] = test_operation_dicts

    def test_eventgroup(self):

        self.assertIsInstance(self.lookup, dict)
        self.assertIsInstance(self.lookup.peerplays, PeerPlays)

        self.assertTrue(self.lookup.parent)
        self.assertTrue(self.lookup.parent_id)
        self.assertEqual(self.lookup.parent["id"], self.lookup.parent_id)

    def test_eventscheme_namecreation(self):
        self.assertIn(
            ['en', 'Demo : Foobar'],
            self.lookup.names
        )
        self.assertIn(
            ['en_us', 'Foobar @ Demo'],
            self.lookup.names
        )

    def test_test_operation_equal(self):
        for x in test_operation_dicts:
            self.assertTrue(self.lookup.test_operation_equal(x))

        with self.assertRaises(ValueError):
            self.assertTrue(self.lookup.test_operation_equal({}))

    def test_find_id(self):
        self.assertEqual(self.lookup.find_id(), this_id)

    def test_is_synced(self):
        self.lookup["id"] = this_id
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

        self.lookup["id"] = this_id
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
            "teams": ["Demo", "Foobar"],
            "eventgroup_identifier": "NFL#PreSeas",
            "sport_identifier": "AmericanFootball",
            "season": {"en": "2017-00-00"},
            "start_time": start_time
        }), LookupEvent)

        with self.assertRaises(ValueError):
            self.assertIsInstance(LookupEvent(**{
                "teams": ["Demo", "Foobar"],
                "eventgroup_identifier": "NFL#PreSeas",
                "sport_identifier": "AmericanFootball",
                "season": {"en": "2017-00-00"},
                "start_time": "SOME STRING"
            }), LookupEvent)

        with self.assertRaises(ValueError):
            self.assertIsInstance(LookupEvent(**{
                "teams": ["Demo", "Foobar", "third TEAM"],
                "eventgroup_identifier": "NFL#PreSeas",
                "sport_identifier": "AmericanFootball",
                "season": {"en": "2017-00-00"},
                "start_time": start_time
            }), LookupEvent)

        with self.assertRaises(TypeError):
            self.assertIsInstance(LookupEvent(**{
                "eventgroup_identifier": "NFL#PreSeas",
                "sport_identifier": "AmericanFootball",
                "season": {"en": "2017-00-00"},
                "start_time": start_time
            }), LookupEvent)

        with self.assertRaises(TypeError):
            self.assertIsInstance(LookupEvent(**{
                "teams": ["Demo", "Foobar"],
                "sport_identifier": "AmericanFootball",
                "season": {"en": "2017-00-00"},
                "start_time": start_time
            }), LookupEvent)

        with self.assertRaises(TypeError):
            self.assertIsInstance(LookupEvent(**{
                "teams": ["Demo", "Foobar"],
                "eventgroup_identifier": "NFL#PreSeas",
                "season": {"en": "2017-00-00"},
                "start_time": start_time
            }), LookupEvent)

        with self.assertRaises(TypeError):
            self.assertIsInstance(LookupEvent({
                "teams": ["Demo", "Foobar"],
                "eventgroup_identifier": "NFL#PreSeas",
                "sport_identifier": "AmericanFootball",
                "start_time": start_time
            }), LookupEvent)

        self.assertIsInstance(self.lookup["teams"], list)
        self.assertEqual(self.lookup["teams"][0], "Demo")
        self.assertEqual(self.lookup["teams"][1], "Foobar")

    def test_find_event(self):
        event = LookupEvent.find_event(
            sport_identifier=miniumum_event_dict["sport_identifier"],
            eventgroup_identifier=miniumum_event_dict["eventgroup_identifier"],
            teams=miniumum_event_dict["teams"],
            start_time=start_time
        )
        self.assertTrue(event)
        self.assertEqual(event["id"], "1.18.0")

    def test_participants(self):
        with self.assertRaises(ValueError):
            LookupEvent(**{
                "teams": ["Demo", "Foobar-Not"],
                "eventgroup_identifier": "NFL#PreSeas",
                "sport_identifier": "AmericanFootball",
                "season": {"en": "2017-00-00"},
                "start_time": start_time
            })

        LookupEvent(**{
            "teams": ["Jets", "Buffy"],
            "eventgroup_identifier": "NFL#PreSeas",
            "sport_identifier": "AmericanFootball",
            "season": {"en": "2017-00-00"},
            "start_time": start_time
        })

    def test_leadtimemax_close(self):
        event = LookupEvent.find_event(
            sport_identifier=miniumum_event_dict["sport_identifier"],
            eventgroup_identifier=miniumum_event_dict["eventgroup_identifier"],
            teams=miniumum_event_dict["teams"],
            start_time=start_time_2
        )
        LookupEventGroup.start_datetime = PropertyMock(
            return_value=datetime.datetime.utcnow() + datetime.timedelta(days=3)
        )
        LookupEventGroup.finish_datetime = PropertyMock(
            return_value=datetime.datetime.utcnow() + datetime.timedelta(days=14)
        )
        LookupEventGroup.leadtime_Max = PropertyMock(return_value=2)
        self.assertFalse(event.can_open)

    def test_leadtimemax_open(self):
        event = LookupEvent.find_event(
            sport_identifier=miniumum_event_dict["sport_identifier"],
            eventgroup_identifier=miniumum_event_dict["eventgroup_identifier"],
            teams=miniumum_event_dict["teams"],
            start_time=miniumum_event_dict["start_time"]
        )
        LookupEventGroup.start_datetime = PropertyMock(
            return_value=datetime.datetime.utcnow() + datetime.timedelta(days=1)
        )
        LookupEventGroup.finish_datetime = PropertyMock(
            return_value=datetime.datetime.utcnow() + datetime.timedelta(days=14)
        )
        LookupEventGroup.leadtime_Max = PropertyMock(return_value=2)
        self.assertTrue(event.can_open)

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
