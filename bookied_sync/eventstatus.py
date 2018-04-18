import datetime
from .lookup import Lookup
from .event import LookupEvent
from peerplays.event import Event, Events
from peerplays.utils import formatTime, parse_time
# from . import log


def subsitution(teams, scheme):
    class Teams:
        home = " ".join([
            x.capitalize() for x in teams[0].split(" ")])
        away = " ".join([
            x.capitalize() for x in teams[1].split(" ")])

    ret = dict()
    for lang, name in scheme.items():
        ret[lang] = name.format(
            teams=Teams
        )
    return ret


class LookupEventStatus(Lookup, dict):
    """ Lookup Class for an Event

        :param list teams: Teams (first element is **HomeTeam**)
        :param str eventgroup_identifier: Identifier of the event group
        :param str sport_identifier: Identifier of the sport
        :param list season: Internationalized string for the season
        :param datetime.datetime start_time: Datetime the event starts
               (required when creating an event)
        :param dict extra_data: Optionally provide additional data that is
               stored in the same dictionary

        ... note:: Please note that the list of teams begins with the **home**
                   team! Only two teams per event are supported!
    """

    operation_update = "event_update_status"
    operation_create = "event_update_status"

    def __init__(
        self,
        event,
        status,
        scores=[],
        id=None,
        extra_data={},
        **kwargs
    ):
        Lookup.__init__(self)
        assert isinstance(event, LookupEvent)
        self.parent = event

        # Also store all the stuff in kwargs
        dict.__init__(self, extra_data)
        dict.update(self, {
            "status": status,
            "scores": scores,
            "event": event})
        self.identifier = "{} -> {}".format(
            event["name"]["en"], status)

    def test_operation_equal(self, op, **kwargs):
        """ This method checks if an object or operation on the blockchain
            has the same content as an object in the  lookup
        """
        if (
            self["event"]["id"] == op["event_id"] and
            self["scores"] == op["scores"] and
            self["status"] == op["status"]
        ):
            return True

    def find_id(self):
        """ Try to find an id for the object of the  lookup on the
            blockchain
        """
        return self["event"]["id"]

    def is_synced(self):
        """ Test if data on chain matches lookup
        """
        event = Event(self["event"]["id"])
        if event["status"] == self["status"]:
            return True

    def propose_new(self):
        """ Propose to update the status of the event
        """
        pass

    def propose_update(self):
        """ Propose to update this object to match  lookup
        """
        return self.peerplays.event_update_status(
            self["event"]["id"],
            status=self["status"],
            scores=self["scores"],
            account=self.proposing_account,
            append_to=Lookup.proposal_buffer
        )
