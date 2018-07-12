from .lookup import Lookup
from .rule import LookupRules
from .exceptions import MissingMandatoryValue
from .utils import dList2Dict
from peerplays.event import Event
from peerplays.rule import Rule
from peerplays.asset import Asset
from peerplays.bettingmarketgroup import (
    BettingMarketGroups, BettingMarketGroup)
from . import log
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
            event.names_json["en"],
            self.description_json["en"]
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
            # We compare only the 'eng' content by default
            LookupBettingMarketGroup.cmp_required_keys(),
            LookupBettingMarketGroup.cmp_status(),
            LookupBettingMarketGroup.cmp_event(),
            LookupBettingMarketGroup.cmp_all_description()
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

            ... note:: This only checks if a sport exists with the same name in
                       **ENGLISH**!
        """
        # In case the parent is a proposal, we won't
        # be able to find an id for a child
        parent_id = self.parent.id
        if not self.valid_object_id(parent_id):
            return

        bmgs = BettingMarketGroups(
            self.parent.id,
            peerplays_instance=self.peerplays)

        find_id_search = kwargs.get("find_id_search", [
            # We compare only the 'eng' content by default
            # 'x' will be the Lookup
            # 'y' will be the content of the on-chain Object!
            LookupBettingMarketGroup.cmp_description("en"),
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
                overunder=self.get("overunder")
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
            overunder=self.get("overunder")
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

    @property
    def description_json(self):
        return dList2Dict(self.description)

    def set_overunder(self, ou):
        self["overunder"] = ou

    def set_handicaps(self, home=None, away=None):
        if away is not None and home is None:
            home = -int(away)
        if away is None and home is not None:
            away = -int(home)
        self["handicaps"] = [home, away]

    @staticmethod
    def cmp_fuzzy(spread=1):
        """ This method returns a method!

            It is used to obtain a compare method that contains a given
            'spread' (allowed threshold) around a center as provide by the
            Lookup
        """
        def cmp(soll, ist):
            def in_range(x, center):
                x = float(x)
                center = float(center)
                return x >= center - spread and x <= center + spread

            ist_description = ist.get("description", ist.get("new_description"))
            if not ist_description:
                return False

            self_description = soll.description_json
            description = dList2Dict(ist_description)
            if "_dynamic" not in self_description or "_dynamic" not in description:
                return False

            if self_description["_dynamic"].lower() != description["_dynamic"]:
                return False

            # Handicap ##########################
            if self_description["_dynamic"].lower() == "hc":
                assert "_hca" in self_description and \
                    "_hch" in self_description and \
                    "_hca" in description and \
                    "_hch" in description, \
                    "dynamic betting market is missing _hca or _hch"

                # Need the handicap of home and away to match fuzzy
                if (
                    in_range(description["_hch"], self_description["_hch"]) and
                    in_range(description["_hca"], self_description["_hca"])
                ):
                    return True

            # Overunder #########################
            elif self_description["_dynamic"].lower() == "ou":
                assert "_ou" in self_description and \
                    "_ou" in description, \
                    "dynamic betting market is missing _overunder"
                return in_range(
                    description["_ou"],
                    self_description["_ou"]
                )

            else:
                raise
        # Return the new cmp function that contains the 'spread'
        return cmp

    @staticmethod
    def cmp_description(key="en"):
        """ This method simply compares the a given description key
            (e.g. 'en')
        """
        def cmp(soll, ist):
            ist_description = ist.get("description", ist.get("new_description"))
            if not ist_description:
                return False

            return [key, soll.description_json.get(key)] in ist_description

        return cmp

    @staticmethod
    def cmp_descriptions(key=["en"]):
        """ This method simply compares the a given description key
            (e.g. 'en')
        """
        def cmp(soll, ist):
            ist_description = ist.get("description", ist.get("new_description"))
            if not ist_description:
                return False
            return all([
                bool([k, soll.description_json.get(k)] in ist_description)
                for k in key
            ])

        return cmp

    @staticmethod
    def cmp_external_descriptions():
        return LookupBettingMarketGroup.cmp_descriptions_key_lambda(lambda x: x[0] != "_")

    @staticmethod
    def cmp_descriptions_key_lambda(f):
        """ This method simply compares the a given description key
            (e.g. 'en')
        """
        def cmp(soll, ist):
            ist_description = ist.get("description", ist.get("new_description"))
            if not ist_description:
                return False

            keys = filter(f, dList2Dict(ist_description).keys())
            return all([
                bool([k, soll.description_json.get(k)] in ist_description)
                for k in keys
            ])

        return cmp

    @staticmethod
    def cmp_all_description():
        def cmp(soll, ist):
            lookupdescr = soll.description
            chainsdescr = ist.get("description", ist.get("new_description"))
            return (
                (bool(chainsdescr) and bool(lookupdescr)) and
                all([a in chainsdescr for a in lookupdescr]) and
                all([b in lookupdescr for b in chainsdescr])
            )
        return cmp

    @staticmethod
    def cmp_required_keys():
        def cmp(soll, ist):
            def is_update(bmg):
                return any([x in bmg for x in [
                    "betting_market_group_id", "new_description",
                    "new_event_id", "new_rules_id"]])

            def is_create(bmg):
                return any([x in bmg for x in [
                    "description", "event_id", "rules_id"]])
            if not is_update(ist) and not is_create(ist):
                raise ValueError
            return is_update(ist) or is_create(ist)
        return cmp

    @staticmethod
    def cmp_status():
        def cmp(soll, ist):
            return (not bool(soll.get("status")) or ist.get("status") == soll.get("status"))
        return cmp

    @staticmethod
    def cmp_event():
        def cmp(soll, ist):
            event_id = ist.get("event_id", ist.get("new_event_id"))
            test_event = soll.valid_object_id(event_id, Event)
            return (not test_event or ist.get("event_id", ist.get("new_event_id")) == soll.event.id)
        return cmp

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
        if not "description" in operation:
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
