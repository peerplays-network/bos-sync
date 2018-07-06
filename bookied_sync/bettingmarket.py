from . import log
from .lookup import Lookup
from .rule import LookupRules
from .utils import dList2Dict
from peerplays.bettingmarket import (
    BettingMarket, BettingMarkets)
from peerplays.bettingmarketgroup import (
    BettingMarketGroup, BettingMarketGroups)


class LookupBettingMarket(Lookup, dict):
    """ Lookup Class for Betting Market

        :param dict description: list of internationalized descriptions
        :param LookupBettingMarketGroup bmg: Parent element
        :param dict extra_data: Optionally provide additional data that is
               stored in the same dictionary

    """
    operation_update = "betting_market_update"
    operation_create = "betting_market_create"

    def __init__(
        self,
        description,
        bmg,
        extra_data={}
    ):
        Lookup.__init__(self)
        self.identifier = "{}/{}".format(
            bmg["description"]["en"],
            description["en"]
        )
        self.bmg = bmg
        self.parent = bmg
        dict.__init__(self, extra_data)
        dict.update(
            self, {
                "description": description
            }
        )

    @property
    def event(self):
        """ Return parent Event
        """
        return self.parent.event

    @property
    def group(self):
        """ Return parent BMG
        """
        return self.parent

    def test_operation_equal(self, bm, **kwargs):
        """ This method checks if an object or operation on the blockchain
            has the same content as an object in the  lookup
        """
        test_operation_equal_search = kwargs.get("test_operation_equal_search", [
            # We compare only the 'eng' content by default
            LookupBettingMarket.cmp_required_keys(),
            LookupBettingMarket.cmp_status(),
            LookupBettingMarket.cmp_group(),
            LookupBettingMarket.cmp_all_description()
        ])

        """ We need to properly deal with the fact that betting markets
            cannot be distinguished alone from the payload if they are bundled
            in a proposal and refer to betting_market_group_id 0.0.x
        """
        group_id = bm.get("group_id", bm.get("new_group_id"))
        test_group = self.valid_object_id(group_id)
        if group_id and not test_group and group_id[0] == "0" and "proposal" in kwargs:
            full_proposal = kwargs.get("proposal")
            if full_proposal:
                operation_id = int(group_id.split(".")[2])
                parent_op = dict(full_proposal)["proposed_transaction"]["operations"][operation_id]
                if not self.parent.test_operation_equal(parent_op[1], proposal=full_proposal):
                    return False

        if all([
            # compare by using 'all' the funcs in find_id_search
            func(self, bm)
            for func in test_operation_equal_search
        ]):
            return True
        return False

    def find_id(self, **kwargs):
        """ Try to find an id for the object of the  lookup on the
            blockchain

            ... note:: This only checks if a sport exists with the
                        same description in **ENGLISH**!
        """
        # In case the parent is a proposal, we won't
        # be able to find an id for a child
        parent_id = self.parent.id
        if not self.valid_object_id(parent_id):
            return

        bms = BettingMarkets(
            self.parent.id,
            peerplays_instance=self.peerplays)

        find_id_search = kwargs.get("find_id_search", [
            # We compare only the 'eng' content by default
            # 'x' will be the Lookup
            # 'y' will be the content of the on-chain Object!
            LookupBettingMarket.cmp_description("en"),
        ])

        for bm in bms:
            if all([
                # compare by using 'all' the funcs in find_id_search
                func(self, bm)
                for func in find_id_search
            ]):
                return bm["id"]

    def is_synced(self):
        """ Test if data on chain matches lookup
        """
        if "id" in self and self["id"]:
            bmg = BettingMarket(self["id"])
            if self.test_operation_equal(bmg):
                return True
        return False

    def propose_new(self):
        """ Propose operation to create this object
        """
        return self.peerplays.betting_market_create(
            description=self.description,
            payout_condition=[],
            group_id=self.parent.id,
            account=self.proposing_account,
            append_to=Lookup.proposal_buffer
        )

    def propose_update(self):
        """ Propose to update this object to match  lookup
        """
        return self.peerplays.betting_market_update(
            self.id,
            payout_condition=[],
            description=self.description,
            group_id=self.parent.id,
            account=self.proposing_account,
            append_to=Lookup.proposal_buffer
        )

    @property
    def description(self):
        """ This method ensures that the description has the proper format as
            well as the proper string replacements for teams
        """
        return [
            [
                k,
                v.format(**self)   # replace variables
            ] for k, v in self["description"].items()
        ]

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
            def is_update(bm):
                return any([x in bm for x in [
                    "new_group_id", "new_description",
                    "betting_market_id"]])

            def is_create(bm):
                return any([x in bm for x in [
                    "group_id", "description"]])

            if not is_create(ist) and not is_update(ist):
                raise ValueError
            return is_update(ist) or is_create(ist)
        return cmp

    @staticmethod
    def cmp_status():
        def cmp(soll, ist):
            return (not bool(soll.get("status")) or ist.get("status") == soll.get("status"))
        return cmp

    @staticmethod
    def cmp_group():
        def cmp(soll, ist):
            group_id = ist.get("group_id", ist.get("new_group_id"))
            test_group = soll.valid_object_id(group_id)
            return (not test_group or ist.get("group_id", ist.get("new_group_id")) == soll.group.id)
        return cmp

    @property
    def description_json(self):
        return dList2Dict(self.description)
