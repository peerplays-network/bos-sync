from .lookup import Lookup
from .rule import LookupRules
from peerplays.bettingmarketgroup import (
    BettingMarketGroup
)
from bookied_sync.utils import dList2Dict
from peerplays.rule import Rule
from .substitutions import substitute_metric


class LookupBettingMarketGroupResolve(Lookup, dict):
    """ Lookup Class for Resolving BettingMarketGroups

        .. note:: If ``result`` is a dictionary, then first element is
            ``homeTeam`` and second is ``awayTeam``.
    """

    operation_update = None
    operation_create = "betting_market_group_resolve"

    def __init__(
        self,
        bmg,
        result,
        handicaps=None,
        overunder=None,
        extra_data={}
    ):
        Lookup.__init__(self)
        self.identifier = "{}::resolution".format(
            dList2Dict(bmg.description)["en"],
        )
        self.parent = bmg
        dict.__init__(self, extra_data)
        dict.update(self, bmg)

        assert isinstance(result, list) and len(result) == 2, \
            "Result must be a list of length 2."
        handicaps = handicaps or [0, 0]
        overunder = overunder or 0
        dict.update(self, dict(
            result=result,
            handicaps=handicaps,
            overunder=overunder
        ))

        # We here direct the handicaps and overunders through BettingMarket
        # Group of the parent and load it from there again to allow
        # modifications according to set_*()
        if overunder:
            self.parent.set_overunder(overunder)
            self["overunder"] = self.parent["overunder"]

        if any(handicaps):
            self.parent.set_handicaps(
                home=handicaps[0],
                away=handicaps[1]
            )
            self["handicaps"] = self.parent["handicaps"]

    @property
    def overunder(self):
        return self.parent["overunder"]

    @property
    def handicaps(self):
        return self.parent["handicaps"]

    @property
    def bmg(self):
        """ The BMG is the parent
        """
        return self.parent

    @property
    def markets(self):
        """ The BMG is the parent
        """
        return self.parent.bettingmarkets

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

    @property
    def grading(self):
        # We take the actual grading from the blockchain and not from
        # the lookup!!
        rule = Rule(self.rules.id, peerplays_instance=self.peerplays)
        return rule.grading

    @property
    def _metric(self):
        return substitute_metric(
            self.grading.get("metric", ""),
            result=self["result"],
            handicaps=self["handicaps"],
            overunder=self["overunder"],
            handicap_allow_float=self.parent.allow_float
        )

    def _equation(self, eq):
        return substitute_metric(
            eq,
            metric=self.metric,
            result=self["result"],
            handicaps=self["handicaps"],
            overunder=self["overunder"],
            handicap_allow_float=self.parent.allow_float
        )

    @property
    def metric(self):
        s = self._metric
        if not isinstance(s, str):
            raise ValueError(
                "metric must be string, was {}".format(
                    type(s)))
        try:
            metric = eval(s)
        except Exception:
            raise Exception("Cannot evaluate metric '{}'".format(s))
        return metric

    def evaluate_metric(self, equation):
        # Define variables we want to use when grading
        if not isinstance(equation, str):
            raise ValueError(
                "equation must be string, was {}".format(
                    type(equation)
                ))
        equation = self._equation(equation)
        try:
            metric = eval(equation)
        except Exception:
            raise Exception("Cannot evaluate metric '{}'".format(equation))
        return metric

    @property
    def resolutions(self):
        """ This property constructs the resultions array to be used in the
            transactions. It takes the following form

            .. code-block:: js

                [
                    ["1.21.257", "win"],
                    ["1.21.258", "not_win"],
                    ["1.21.259", "cancel"],
                ]

        """
        bettingmarkets = self.markets
        ret = []
        for market in self.grading.get("resolutions", []):
            bettingmarket = next(bettingmarkets)

            resolved = {
                key: self.evaluate_metric(equation)
                for key, equation in market.items()
            }
            # The resolved dictionary looks like this
            # {'win': False, 'not_win': True, 'void': False}
            # we now need to ensure that only one of those options is 'true'
            assert sum(resolved.values()) == 1, \
                "Multiple or no options resolved to 'True': {}".format(
                    str(resolved))

            ret.extend([
                [bettingmarket.id, key]
                for key, value in resolved.items() if value
            ])

        return ret

    def test_operation_equal(self, resolve, **kwargs):
        """ This method checks if an object or operation on the blockchain
            has the same content as an object in the  lookup
        """

        lookupresults = self.resolutions
        chainsresults = resolve["resolutions"]
        bmg_id = resolve["betting_market_group_id"]

        # Test if BMG exists
        test_bmg = self.valid_object_id(bmg_id, BettingMarketGroup)

        if (
            all([a in chainsresults for a in lookupresults]) and
            all([b in lookupresults for b in chainsresults]) and
            (not test_bmg or bmg_id == self.parent_id)
        ):
            return True
        return False

    def find_id(self):
        """ Market resolve operations do not have their own ids
        """
        pass

    def is_synced(self):
        """ Here, we need to figure out if the market has already been resolved
        """
        # FIXME  / TODO
        return False

    def propose_new(self):
        """ This call proposes the resolution of the betting market group
        """
        return self.peerplays.betting_market_resolve(
            self.parent_id,
            self.resolutions,
            account=self.proposing_account,
            append_to=Lookup.proposal_buffer
        )

    def propose_update(self):
        """ There is no such thing as an updated resolution
        """
        pass
