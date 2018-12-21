import unittest
from copy import deepcopy
from peerplays.event import Event
from bookied_sync.utils import dList2Dict
from bookied_sync import comparators
from bookied_sync.bettingmarketgroup import LookupBettingMarketGroup
from bookied_sync.bettingmarketgroupresolve import LookupBettingMarketGroupResolve
from .fixtures import fixture_data, config, lookup_test_event

event_id = "1.22.2242"
bmg_id = "1.24.213"
test_operation_dict = {
    "id": bmg_id,
    "description": [
        ["display_name", "HC (0:1)"],
        ["en", "Handicap (0:1)"],
        ["sen", "Handicap (0:1)"],
        ["_dynamic", "hc"],
        ["_hch", "1"],
        ["_hca", "-1"],
    ],
    "event_id": "0.0.0",
    "rules_id": "1.23.10",
    "asset_id": "1.3.0",
    "status": "ongoing",
}


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fixture_data()

        self.event = lookup_test_event(event_id)
        self.lookup = list(self.event.bettingmarketgroups)[1]

        # Set the variable that disallows for float handicaps
        self.lookup["dynamic_allow_float"] = False

        self.lookup.set_handicaps(home=1)

    def test_init(self):
        self.assertIsInstance(self.lookup, LookupBettingMarketGroup)

    def test_set_handicap(self):
        self.assertEqual(self.lookup["handicaps"], [1, -1])

    def test_bmg_names(self):
        self.assertIn(["en", "Handicap (0:1)"], self.lookup.description)

    def test_bms_names(self):
        bms = list(self.lookup.bettingmarkets)
        names_home = bms[0].description
        names_away = bms[1].description
        self.assertIn(["en", "Atlanta Hawks (1)"], names_home)
        # self.assertIn(['handicap', '1'], names_home)
        self.assertIn(["en", "Boston Celtics (-1)"], names_away)
        # self.assertIn(['handicap', '-1'], names_away)

    def test_test_operation_equal(self):
        self.assertTrue(self.lookup.test_operation_equal(test_operation_dict))

        with self.assertRaises(ValueError):
            self.assertTrue(self.lookup.test_operation_equal({}))

    def test_find_id(self):
        self.assertEqual(self.lookup.find_id(), bmg_id)

    def test_is_synced(self):
        self.lookup["id"] = bmg_id
        self.assertTrue(self.lookup.is_synced())

    def test_propose_new(self):
        from peerplaysbase.operationids import operations

        self.lookup.clear_proposal_buffer()
        tx = self.lookup.propose_new()
        tx = tx.json()
        self.assertIsInstance(tx, dict)
        self.assertIn("operations", tx)
        self.assertIn("ref_block_num", tx)
        self.assertEqual(tx["operations"][0][0], 22)
        self.assertEqual(
            tx["operations"][0][1]["proposed_ops"][0]["op"][0],
            operations[self.lookup.operation_create],
        )

    def test_propose_update(self):
        from peerplaysbase.operationids import operations

        self.lookup["id"] = bmg_id
        self.lookup.clear_proposal_buffer()
        tx = self.lookup.propose_update()
        tx = tx.json()
        self.assertIsInstance(tx, dict)
        self.assertIn("operations", tx)
        self.assertIn("ref_block_num", tx)
        self.assertEqual(tx["operations"][0][0], 22)
        self.assertEqual(
            tx["operations"][0][1]["proposed_ops"][0]["op"][0],
            operations[self.lookup.operation_update],
        )

    def assertResult(self, resolutions, *results):
        self.assertEqual(len(results), len(resolutions))
        for r in results:
            self.assertIn(r, resolutions)

    def test_result_00_on_10(self):
        resolve = LookupBettingMarketGroupResolve(self.lookup, [0, 0], handicaps=[1, 0])
        self.assertEqual(resolve.bmg["handicaps"], [1, -1])
        self.assertEqual(resolve._metric, "(0 + 0) - (0 + 1)")
        self.assertEqual(resolve.metric, -1)
        self.assertResult(
            resolve.resolutions, ["1.25.2952", "not_win"], ["1.25.2953", "win"]
        )

    def test_result_01_on_10(self):
        resolve = LookupBettingMarketGroupResolve(self.lookup, [0, 1], handicaps=[1, 0])
        self.assertEqual(resolve._metric, "(0 + 0) - (1 + 1)")
        self.assertEqual(resolve.metric, -2)
        self.assertResult(
            resolve.resolutions, ["1.25.2952", "not_win"], ["1.25.2953", "win"]
        )

    def test_result_10_on_10(self):
        resolve = LookupBettingMarketGroupResolve(self.lookup, [1, 0], handicaps=[1, 0])
        self.assertEqual(resolve._metric, "(1 + 0) - (0 + 1)")
        self.assertEqual(resolve.metric, 0)
        self.assertResult(
            resolve.resolutions, ["1.25.2952", "not_win"], ["1.25.2953", "not_win"]
        )

    def test_result_20_on_10(self):
        resolve = LookupBettingMarketGroupResolve(self.lookup, [2, 0], handicaps=[1, 0])
        self.assertEqual(resolve._metric, "(2 + 0) - (0 + 1)")
        self.assertEqual(resolve.metric, 1)
        self.assertResult(
            resolve.resolutions, ["1.25.2952", "win"], ["1.25.2953", "not_win"]
        )

    def test_result_00_on_20(self):
        self.lookup.set_handicaps(home=2)
        resolve = LookupBettingMarketGroupResolve(self.lookup, [0, 0], handicaps=[2, 0])
        self.assertEqual(resolve._metric, "(0 + 0) - (0 + 2)")
        self.assertEqual(resolve.metric, -2)
        self.assertResult(
            resolve.resolutions, ["1.25.2954", "not_win"], ["1.25.2955", "win"]
        )

    def test_find_fuzzy_market(self):
        self.lookup.set_handicaps(home=5)

        self.assertEqual(
            self.lookup.find_id(
                find_id_search=[
                    lambda x, y: ["en", dList2Dict(x.description)["en"]]
                    in y["description"]
                ]
            ),
            "1.24.220",
        )

        self.assertEqual(
            self.lookup.find_id(find_id_search=[comparators.cmp_fuzzy(0)]), "1.24.220"
        )

        self.lookup.set_handicaps(home=6.5)
        self.assertFalse(self.lookup.find_id(find_id_search=[comparators.cmp_fuzzy(0)]))

        self.assertFalse(
            self.lookup.find_id(find_id_search=[comparators.cmp_fuzzy(0.49)])
        )

        self.assertTrue(
            self.lookup.find_id(find_id_search=[comparators.cmp_fuzzy(0.5)])
        )

        self.assertTrue(
            self.lookup.find_id(find_id_search=[comparators.cmp_fuzzy(0.51)])
        )

    def test_fuzzy_operation_compare(self):
        self.assertTrue(
            self.lookup.test_operation_equal(
                test_operation_dict,
                test_operation_equal_search=[
                    comparators.cmp_required_keys(
                        ["description", "event_id", "rules_id"]
                    ),
                    comparators.cmp_status(),
                    comparators.cmp_event(),
                    comparators.cmp_all_description(),
                ],
            )
        )
        t2 = deepcopy(test_operation_dict)
        t2["description"] = [["en", "Handicap (0:1)"]]
        self.assertFalse(
            self.lookup.test_operation_equal(
                t2, test_operation_equal_search=[comparators.cmp_all_description()]
            )
        )
        self.assertTrue(
            self.lookup.test_operation_equal(
                t2, test_operation_equal_search=[comparators.cmp_description("en")]
            )
        )
