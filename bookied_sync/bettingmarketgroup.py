import math
from .lookup import Lookup
from .rule import LookupRules
from .exceptions import MissingMandatoryValue
from .utils import dList2Dict
from peerplays.event import Event
from peerplays.rule import Rule
from peerplays.asset import Asset
from peerplays.bettingmarketgroup import (
    BettingMarketGroups, BettingMarketGroup)
from . import log, comparators
from .substitutions import substitute_bettingmarket_name


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
        self.event = event
        self.parent = event
        # Let's predefine dynamic matrial
        dict.__init__(self, extra_data)
        dict.update(self, dict(
            handicaps=[0, 0],
            overunder=0
        ))
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
        self.identifier = "{}/{}".format(
            dList2Dict(event.names)["en"],
            dList2Dict(self.description)["en"]
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
        test_operation_equal_search = kwargs.get("test_operation_equal_search", [
            comparators.cmp_required_keys([
                "betting_market_group_id", "new_description",
                "new_event_id", "new_rules_id"
            ], [
                "betting_market_group_id", "description",
                "event_id", "rules_id"
            ]),
            comparators.cmp_status(),
            comparators.cmp_event(),
            comparators.cmp_all_description()
        ])

        """ We need to properly deal with the fact that betting market groups
            cannot be distinguished alone from the payload if they are bundled
            in a proposal and refer to event_id 0.0.x
        """
        event_id = bmg.get("event_id", bmg.get("new_event_id"))
        test_event = self.valid_object_id(event_id, Event)
        if event_id and not test_event and event_id[0] == "0" and "proposal" in kwargs:
            full_proposal = kwargs.get("proposal", {})
            if full_proposal:
                operation_id = int(event_id.split(".")[2])
                parent_op = dict(full_proposal)["proposed_transaction"]["operations"][operation_id]
                if not self.parent.test_operation_equal(parent_op[1], proposal=full_proposal):
                    return False

        if all([
            # compare by using 'all' the funcs in find_id_search
            func(self, bmg)
            for func in test_operation_equal_search
        ]):
            """ This is special!

                Since we allow fuzzy logic for matching dynamic parameters, we
                need to pass back the dynamic parameter in case we found a
                object on chain or as a proposal that matches our criteria
                here.

            """
            if self.is_dynamic(bmg):
                self.set_dynamic(bmg)
            return True
        return False

    def find_id(self, **kwargs):
        """ Try to find an id for the object of the  lookup on the
            blockchain

            .. note:: This only checks if a sport exists with the same name in
                       **ENGLISH**!
        """
        # In case the parent is a proposal, we won't
        # be able to find an id for a child
        parent_id = self.parent_id
        if not self.valid_object_id(parent_id):
            return

        bmgs = BettingMarketGroups(
            self.parent_id,
            peerplays_instance=self.peerplays)

        find_id_search = kwargs.get("find_id_search", [
            # We compare only the 'eng' content by default
            comparators.cmp_description("en"),
        ])

        for bmg in bmgs:
            if all([
                # compare by using 'all' the funcs in find_id_search
                func(self, bmg)
                for func in find_id_search
            ]):
                """ This is special!

                    Since we allow fuzzy logic for matching dynamic parameters, we
                    need to pass back the dynamic parameter in case we found a
                    object on chain or as a proposal that matches our criteria
                    here.

                """
                if self.is_dynamic(bmg):
                    self.set_dynamic(bmg)
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
            description = substitute_bettingmarket_name(
                market["description"],
                teams=self.event["teams"],
                handicaps=self.get("handicaps"),
                overunder=self.get("overunder"),
                handicap_allow_float=self.allow_float
            )

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
        description = substitute_bettingmarket_name(
            self["description"],
            teams=self.event["teams"],
            handicaps=self.get("handicaps"),
            overunder=self.get("overunder"),
            handicap_allow_float=self.allow_float
        )
        if self.get("dynamic") == "hc":
            description["_dynamic"] = "hc"
            description["_hch"] = str(self.get("handicaps")[0])
            description["_hca"] = str(self.get("handicaps")[1])

        if self.get("dynamic") == "ou":
            description["_dynamic"] = "ou"
            description["_ou"] = str(self.get("overunder"))

        return [
            [
                k,
                v
            ] for k, v in description.items()
        ]

    def set_overunder(self, ou):
        self["overunder"] = math.floor(float(ou)) + 0.5

    @property
    def allow_float(self):
        """ This attribute is used to switch between integer and float
            handicaps. The difference is that in case of interger, the
            marketgroup might need a 'draw' market as well
        """
        return self.get("dynamic_allow_float", True)

    def set_handicaps(self, home=None, away=None):
        """ This sets symmetric values for "home" and "away". Hence, the
            handicaps are individual to their correspoending team.

            home team with handicap of +1 is equivalent with away team with handicap -1

            Hence, the list would be [+1, -1] and has to always be symmetric
        """
        if (home is None and away is not None) or float(home) == 0.0:
            if self.allow_float:
                away = math.copysign(math.floor(math.fabs(float(away))) + 0.5, float(away))
            else:
                away = float(away)

            home = -away   # Symmetry

        elif (away is None and home is not None) or float(away) == 0.0:
            away = 0
            if self.allow_float:
                home = math.copysign(math.floor(math.fabs(float(home))) + 0.5, float(home))
            else:
                home = int(float(home))

            away = -home  # Symmetry

        else:
            raise

        self["handicaps"] = [home, away]

    @staticmethod
    def is_dynamic_type(x, typ):
        if LookupBettingMarketGroup.is_hc_type(typ):
            return LookupBettingMarketGroup.is_hc_type(x)
        else:
            return LookupBettingMarketGroup.is_ou_type(x)

    @staticmethod
    def is_hc_type(x):
        return x == "hc" or x == "1x2_hc"

    @staticmethod
    def is_ou_type(x):
        return x == "ou"

    def is_dynamic(self, operation):
        if "description" not in operation:
            return False
        description = dList2Dict(operation["description"])
        return "_dynamic" in description

    def set_dynamic(self, operation):
        """ This method is used to obtain dynamic parameters from existing
            proposals and objects and direct them back into lookup
        """
        description = dList2Dict(operation["description"])
        if "_dynamic" in description:
            if (
                LookupBettingMarketGroup.is_hc_type(description["_dynamic"]) and
                "_hch" in description
            ):
                log.info("Setting handicap: {}".format(description["_hch"]))
                self.set_handicaps(home=description["_hch"])
            elif (
                LookupBettingMarketGroup.is_ou_type(description["_dynamic"]) and
                "_ou" in description
            ):
                log.info("Setting overunder: {}".format(description["_ou"]))
                self.set_overunder(description["_ou"])
