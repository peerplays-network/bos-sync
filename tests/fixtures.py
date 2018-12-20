import os
import yaml
import datetime

from dateutil.parser import parse

from peerplays import PeerPlays
from peerplays.instance import set_shared_peerplays_instance
from peerplays.sport import Sports, Sport
from peerplays.event import Events, Event
from peerplays.rule import Rules, Rule
from peerplays.proposal import Proposals, Proposal
from peerplays.eventgroup import EventGroups, EventGroup
from peerplays.bettingmarketgroup import BettingMarketGroups, BettingMarketGroup
from peerplays.bettingmarket import BettingMarkets, BettingMarket
from peerplays.witness import Witnesses, Witness
from peerplaysbase.operationids import operations

from bookied_sync.lookup import Lookup
from bookied_sync.eventgroup import LookupEventGroup
from bookied_sync.event import LookupEvent

# default wifs key for testing
wifs = [
    "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3",
    "5KCBDTcyDqzsqehcb52tW5nU6pXife6V2rX9Yf7c3saYSzbDZ5W",
]
wif = wifs[0]
core_unit = "TEST"

# peerplays instance
peerplays = PeerPlays(
    "wss://api.ppy-beatrice.blckchnd.com", keys=wifs, nobroadcast=True, num_retries=1
)
config = peerplays.config

# Set defaults
peerplays.set_default_account("init0")
set_shared_peerplays_instance(peerplays)

# Ensure we are not going to transaction anythin on chain!
assert peerplays.nobroadcast

# Setup base lookup
lookup = Lookup(
    proposer="init0",
    blockchain_instance=peerplays,
    network="unittests",
    sports_folder=os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "bookiesports"
    ),
)
# ensure lookup isn't broadcasting either
assert lookup.blockchain.nobroadcast


def lookup_new_event():
    return LookupEvent(
        **{
            "teams": ["Miami Heat", "New Orleans Pelicans"],
            "event_group_id": "1.21.12",
            "eventgroup_identifier": "NBA",
            "sport_identifier": "Basketball",
            "season": {"en": "2017-00-00"},
            "start_time": parse("2022-10-16T00:00:00"),
            "status": "upcoming",
        }
    )


def lookup_test_event(id):
    return LookupEvent(
        **{
            "id": "1.22.2242",
            "teams": ["Atlanta Hawks", "Boston Celtics"],
            "eventgroup_identifier": "NBA",
            "sport_identifier": "Basketball",
            "season": {"en": "2017-00-00"},
            "start_time": parse("2022-10-16T00:00:00"),
            "status": "upcoming",
        }
    )


def lookup_test_eventgroup(id):
    return LookupEventGroup("Basketball", "NBA")


def add_event(data):
    if "event_group_id" in data:
        Events._cache[data["event_group_id"]].append(data)


def fixture_data():
    peerplays.clear()
    BettingMarkets.clear_cache()
    Rules.clear_cache()
    BettingMarketGroups.clear_cache()
    Proposals.clear_cache()
    Witnesses.clear_cache()
    Events.clear_cache()
    EventGroups.clear_cache()
    Sports.clear_cache()

    with open(os.path.join(os.path.dirname(__file__), "fixtures.yaml")) as fid:
        data = yaml.safe_load(fid)

    Witnesses._import([Witness(x) for x in data.get("witnesses", [])])
    Sports._import([Sport(x) for x in data.get("sports", [])])
    EventGroups._import([EventGroup(x) for x in data.get("eventgroups", [])])
    Events._import([Event(x) for x in data.get("events", [])])
    BettingMarketGroups._import(
        [BettingMarketGroup(x) for x in data.get("bettingmarketgroups", [])]
    )
    BettingMarkets._import([BettingMarket(x) for x in data.get("bettingmarkets", [])])
    Rules._import([Rule(x) for x in data.get("rules", [])])

    proposals = []
    for proposal in data.get("proposals", []):
        ops = list()
        for _op in proposal["operations"]:
            for opName, op in _op.items():
                ops.append([operations[opName], op])
        # Proposal!
        proposal_id = proposal["proposal_id"]
        proposal_data = {
            "available_active_approvals": [],
            "available_key_approvals": [],
            "available_owner_approvals": [],
            "expiration_time": "2018-05-29T10:23:13",
            "id": proposal_id,
            "proposed_transaction": {
                "expiration": "2018-05-29T10:23:13",
                "extensions": [],
                "operations": ops,
                "ref_block_num": 0,
                "ref_block_prefix": 0,
            },
            "proposer": "1.2.7",
            "required_active_approvals": ["1.2.1"],
            "required_owner_approvals": [],
        }
        proposals.append(Proposal(proposal_data))

    Proposals._import(proposals, "1.2.1")
    Proposals._import(proposals, "witness-account")
