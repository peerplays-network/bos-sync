from .lookup import Lookup
from peerplays.rule import Rules, Rule
from . import log, comparators


class LookupRule(Lookup, dict):
    """ Lookup Class for Rule

        :param str sport: Sport Identifier
        :param str rules: Rules Identifier
    """

    operation_update = "betting_market_rules_update"
    operation_create = "betting_market_rules_create"

    def __init__(self, sport, rules):
        self.identifier = "{}/{}".format(sport, rules)
        Lookup.__init__(self)
        assert sport in self.data["sports"], "Sport {} not avaialble".format(
            sport
        )
        assert rules in self.data["sports"][sport]["rules"], \
            "rules {} not avaialble in sport {}".format(
                rules, sport)
        # This is a list and not a dictionary!
        dict.__init__(
            self,
            self.data["sports"][sport]["rules"][rules]
        )

    def test_operation_equal(self, operation, **kwargs):
        """ This method checks if an object or operation on the blockchain
            has the same content as an object in the  lookup
        """
        test_operation_equal_search = kwargs.get("test_operation_equal_search", [
            comparators.cmp_required_keys([
                "new_description", "new_name"
            ], [
                "description", "name"
            ]),
            comparators.cmp_all_description(),
            comparators.cmp_all_name(),
        ])

        if all([
            # compare by using 'all' the funcs in find_id_search
            func(self, operation)
            for func in test_operation_equal_search
        ]):
            return True
        return False

    def find_id(self, **kwargs):
        """ Try to find an id for the object of the  lookup on the
            blockchain

            .. note:: This only checks if a sport exists with the same name in
                       **ENGLISH**!
        """
        rules = Rules(peerplays_instance=self.peerplays)
        find_id_search = kwargs.get("test_operation_equal_search", [
            comparators.cmp_name("en"),
        ])
        for rule in rules:
            if all([
                # compare by using 'all' the funcs in find_id_search
                func(self, rule)
                for func in find_id_search
            ]):
                return rule["id"]

    def is_synced(self):
        """ Test if data on chain matches lookup
        """
        if "id" in self and self["id"]:
            rule = Rule(self["id"])
            if self.test_operation_equal(rule):
                return True
        return False

    def propose_new(self):
        """ Propose operation to create this object
        """
        return self.peerplays.betting_market_rules_create(
            self.names,
            self.descriptions,
            account=self.proposing_account,
            append_to=Lookup.proposal_buffer
        )

    def propose_update(self):
        """ Propose to update this object to match  lookup
        """
        return self.peerplays.betting_market_rules_update(
            self["id"],
            names=self.names,
            descriptions=self.descriptions,
            account=self.proposing_account,
            append_to=Lookup.proposal_buffer
        )

    @property
    def name(self):
        """ Alias for `names`
        """
        return self.names

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
    def description(self):
        """ Alias for `descriptions`
        """
        return self.descriptions

    @property
    def descriptions(self):
        """ Properly format descriptions for internal use
        """

        # For sake of transparency, we store the grading on the blockchain too
        #
        import json
        grading = json.dumps(self["grading"], sort_keys=True)
        data = self["description"]
        data.update(dict(grading=grading))
        return [
            [
                k.strip(),
                v.strip()
            ] for k, v in data.items()
        ]


class LookupRules(LookupRule):
    """ Legacy compatibility
    """
    pass
