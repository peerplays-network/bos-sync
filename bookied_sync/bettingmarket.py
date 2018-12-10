from . import log
from .lookup import Lookup
from .rule import LookupRules
from .utils import dList2Dict
from peerplays.bettingmarket import (
    BettingMarket, BettingMarkets)
from peerplays.bettingmarketgroup import (
    BettingMarketGroup, BettingMarketGroups)
from . import comparators


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
            comparators.cmp_required_keys([
                "new_group_id", "new_description",
                "betting_market_id"
            ], [
                "group_id", "description",
                "betting_market_id"
            ]),
            comparators.cmp_status(),
            comparators.cmp_group(),
            comparators.cmp_all_description()
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

            .. note:: This only checks if a sport exists with the
                        same description in **ENGLISH**!
        """
        # In case the parent is a proposal, we won't
        # be able to find an id for a child
        parent_id = self.parent_id
        if not self.valid_object_id(parent_id):
            return

        bms = BettingMarkets(
            self.parent_id,
            peerplays_instance=self.peerplays)

        find_id_search = kwargs.get("find_id_search", [
            # We compare only the 'eng' content by default
            comparators.cmp_description("en"),
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
            group_id=self.parent_id,
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
            group_id=self.parent_id,
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
