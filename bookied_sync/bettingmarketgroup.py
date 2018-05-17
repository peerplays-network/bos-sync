from .lookup import Lookup
from .rule import LookupRules
from .exceptions import MissingMandatoryValue
from peerplays.event import Event
from peerplays.rule import Rule
from peerplays.asset import Asset
from peerplays.bettingmarketgroup import (
    BettingMarketGroups, BettingMarketGroup)
from . import log


def substitution(teams, scheme):
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


class LookupBettingMarketGroup(Lookup, dict):
    """ Lookup Class for betting market groups

        :param dict bmg: Lookup content (files) for the BMG
        :param LookupEvent event: Parent LookupEvent for BMG
        :param dict extra_data: Optionally provide additional data that is
               stored in the same dictionary

    """

    operation_update = "betting_market_group_update"
    operation_create = "betting_market_group_create"

    def __init__(
        self,
        bmg,
        event,
        extra_data={}
    ):
        Lookup.__init__(self)
        self.identifier = "{}/{}".format(
            event.names_json["en"],
            bmg["description"]["en"]
        )
        self.event = event
        self.parent = event
        dict.__init__(self, extra_data)
        dict.update(
            self,
            bmg
        )
        for mandatory in [
            "description",
            "asset",
            "bettingmarkets",
            "rules",
        ]:
            if mandatory not in self:
                raise MissingMandatoryValue(
                    "A value for '{}' is mandatory".format(
                        mandatory
                    )
                )

    @property
    def sport(self):
        """ Return the sport for this BMG
        """
        return self.parent.sport

    @property
    def rules(self):
        """ Return instance of LookupRules for this BMG
        """
        assert self["rules"] in self.sport["rules"]
        return LookupRules(self.sport["identifier"], self["rules"])

    def test_operation_equal(self, bmg, **kwargs):
        """ This method checks if an object or operation on the blockchain
            has the same content as an object in the  lookup
        """
        def is_update(bmg):
            return any([x in bmg for x in [
                "betting_market_group_id", "new_description",
                "new_event_id", "new_rules_id"]])

        def is_create(bmg):
            return any([x in bmg for x in [
                "description", "event_id", "rules_id"]])

        if not is_create(bmg) and not is_update(bmg):
            raise ValueError

        lookupdescr = self.description
        chainsdescr = [[]]
        prefix = "new_" if is_update(bmg) else ""
        chainsdescr = bmg.get(prefix + "description")
        rules_id = bmg.get(prefix + "rules_id")
        event_id = bmg.get(prefix + "event_id")
        # Fixme: sync object to also include the proper status
        status = bmg.get("status")

        # Test if Rules and Events exist
        # only if the id starts with 1.
        test_rule = rules_id and rules_id[0] == "1"
        if test_rule:
            Rule(rules_id)

        test_event = event_id and event_id[0] == "1"
        if test_event:
            Event(event_id)

        test_status = bool(self.get("status"))

        """ We need to properly deal with the fact that betting market groups
            cannot be distinguished alone from the payload if they are bundled
            in a proposal and refer to event_id 0.0.x
        """
        if event_id and not test_event and event_id[0] == "0" and "proposal" in kwargs:
            full_proposal = kwargs.get("proposal", {})
            if full_proposal:
                operation_id = int(event_id.split(".")[2])
                parent_op = dict(full_proposal)["proposed_transaction"]["operations"][operation_id]
                if not self.parent.test_operation_equal(parent_op[1], proposal=full_proposal):
                    return False

        if (
            all([a in chainsdescr for a in lookupdescr]) and
            all([b in lookupdescr for b in chainsdescr]) and
            (not test_event or event_id == self.event.id) and
            # FIXME: This needs to be properly tested by unit tests, for some
            # reasons this does sometimes fail to match
            # (not test_rule or rules_id == self.rules.id) and
            (not test_status or status == self.get(status))
        ):
            return True
        return False

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

        bmgs = BettingMarketGroups(
            self.parent.id,
            peerplays_instance=self.peerplays)
        en_descrp = next(filter(lambda x: x[0] == "en", self.description))

        for bmg in bmgs:
            if en_descrp in bmg["description"]:
                return bmg["id"]

    def is_synced(self):
        """ Test if data on chain matches lookup
        """
        if "id" in self and self["id"]:
            bmg = BettingMarketGroup(self["id"])
            if self.test_operation_equal(bmg):
                return True
        return False

    def propose_new(self):
        """ Propose operation to create this object
        """
        asset = Asset(
            self["asset"],
            peerplays_instance=self.peerplays)
        return self.peerplays.betting_market_group_create(
            self.description,
            event_id=self.event.id,
            rules_id=self.rules.id,
            asset=asset["id"],
            delay_before_settling=self.get("delay_before_settling", 0),
            never_in_play=self.get("never_in_play", False),
            account=self.proposing_account,
            append_to=Lookup.proposal_buffer
        )

    def propose_update(self):
        """ Propose to update this object to match  lookup
        """
        return self.peerplays.betting_market_group_update(
            self.id,
            self.description,
            event_id=self.event.id,
            rules_id=self.rules.id,
            status=self.get("status"),
            account=self.proposing_account,
            append_to=Lookup.proposal_buffer
        )

    @property
    def bettingmarkets(self):
        """ Return instances of LookupBettingMarket for this BMG
        """

        from .bettingmarket import LookupBettingMarket

        bm_counter = 0
        for market in self["bettingmarkets"]:
            bm_counter += 1
            # Overwrite the description with with proper replacement of variables
            description = substitution(self.event["teams"], market["description"])

            # Yield one Lookup per betting market
            yield LookupBettingMarket(
                description=description,
                bmg=self
            )

        if bm_counter != int(self["number_betting_markets"]):
            log.critical(
                "We have created a different number of betting markets in "
                "Event: {} / BMG: {} / {}!={}".format(
                    self.parent["name"]["en"],
                    self["description"]["en"],
                    bm_counter, self["number_betting_markets"]
                )
            )

    @property
    def description(self):
        """ Properly format description for internal use
        """
        return [
            [
                k,
                v
            ] for k, v in self["description"].items()
        ]
