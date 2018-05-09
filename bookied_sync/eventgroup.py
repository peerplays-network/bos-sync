import re
import sys
from peerplays.eventgroup import EventGroups, EventGroup
from .lookup import Lookup
from .exceptions import ObjectNotFoundInLookup
from . import log


class LookupEventGroup(Lookup, dict):
    """ Lookup Class for Event Group

        :param str sport: Identifier of the Sport
        :param str eventgroup: Identifier of the Eventgroup

    """

    operation_update = "event_group_update"
    operation_create = "event_group_create"

    def __init__(self, sport, eventgroup):
        from .sport import LookupSport
        self.identifier = eventgroup

        if isinstance(sport, LookupSport):
            sport = sport.get("identifier")

        self.sport_name = sport
        self.sport = LookupSport(sport)
        self.parent = self.sport
        self.eventgroup = eventgroup
        super(LookupEventGroup, self).__init__()

        if eventgroup.lower() in self.data["sports"][sport]["eventgroups"]:
            dict.__init__(
                self,
                self.data["sports"][sport]["eventgroups"][eventgroup]
            )
        else:
            found = False
            for name, evg in self.data["sports"][sport]["eventgroups"].items():
                if (
                    # Name
                    name.lower() == eventgroup.lower() or
                    # Identifier
                    evg.get("identifier", "").lower() == eventgroup.lower() or
                    # List of languages
                    eventgroup.lower() in [
                        x.lower()for x in evg.get("name", {}).values()] or
                    # List of aliases
                    eventgroup.lower() in [
                        x.lower() for x in evg.get("aliases", [])]
                ):
                    found = True
                    dict.__init__(self, evg)

            if not found:
                raise ObjectNotFoundInLookup(
                    "Eventgroup {} not available in sport {}".format(
                        eventgroup, sport))

    def test_operation_equal(self, eventgroup, **kwargs):
        """ This method checks if an object or operation on the blockchain
            has the same content as an object in the  lookup
        """
        lookupnames = self.names
        chainsnames = [[]]
        if "name" in eventgroup:
            chainsnames = eventgroup["name"]
            sport_id = eventgroup["sport_id"]
        elif "new_name" in eventgroup:
            chainsnames = eventgroup["new_name"]
            sport_id = eventgroup["new_sport_id"]
        else:
            raise ValueError

        parts = sport_id.split(".")
        assert len(parts) == 3,\
            "{} is a strange sport object id".format(sport_id)
        if int(parts[0]) == 0:
            sport_id = ""

        if (all([a in chainsnames for a in lookupnames]) and
                all([b in lookupnames for b in chainsnames]) and
                (not sport_id or self.parent.id == sport_id)):
            return True

    def find_id(self):
        """ Try to find an id for the object of the  lookup on the
            blockchain

            ... note:: This only checks if a sport exists with the same name in
                       **ENGLISH**!
        """
        # In case the parent is a proposal, we won't
        # be able to find an id for a child
        parent_id = self.parent.id
        if parent_id[0] == "0" or parent_id[:4] == "1.10":
            return

        egs = EventGroups(
            self.parent.id,
            peerplays_instance=self.peerplays)
        en_descrp = next(filter(lambda x: x[0] == "en", self.names))

        for eg in egs:
            if (
                en_descrp in eg["name"] and
                self.parent.id == eg["sport_id"]
            ):
                return eg["id"]

    def is_synced(self):
        """ Test if data on chain matches lookup
        """
        if "id" in self and self["id"]:
            eventgroup = EventGroup(self["id"])
            if self.test_operation_equal(eventgroup):
                return True
        return False

    def propose_new(self):
        """ Propose operation to create this object
        """
        return self.peerplays.event_group_create(
            self.names,
            sport_id=self.parent_id,
            account=self.proposing_account,
            append_to=Lookup.proposal_buffer
        )

    def propose_update(self):
        """ Propose to update this object to match  lookup
        """
        return self.peerplays.event_group_update(
            self["id"],
            names=self.names,
            sport_id=self.parent_id,
            account=self.proposing_account,
            append_to=Lookup.proposal_buffer
        )

    @property
    def names(self):
        """ Properly format names for internal use
        """
        names = self["name"]
        names.update({"identifier": self["identifier"]})
        return [
            [
                k,
                v
            ] for k, v in names.items()
        ]

    @property
    def is_open(self):
        """ Only update if after leadtime
        """
        # Today, we only distinguish events through the dates,
        # not prevent them from being created
        return True

        # from datetime import datetime, timedelta
        # now = datetime.utcnow()
        # start_date = datetime.strptime(self.get("start_date"), "%Y/%m/%d")
        # finish_date = datetime.strptime(self.get("finish_date"), "%Y/%m/%d")
        # return (
        #     now > start_date and
        #     now < finish_date
        # )

    @property
    def start_datetime(self):
        return self.get("start_date")

    @property
    def finish_datetime(self):
        return self.get("finish_date")

    @property
    def leadtime_Max(self):
        return self.get("leadtime_Max")
