import mock
import logging
import unittest

from .fixtures import fixture_data, lookup_test_event, lookup_new_event
from peerplaysapi.exceptions import OperationInProposalExistsException

logging.basicConfig(level=logging.INFO)


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()

    def test_retrigger_update(self):
        lookup = lookup_test_event("1.18.2242")
        lookup["status"] = "finished"
        with mock.patch("bookied_sync.event.LookupEvent.propose_update") as m:
            m.side_effect = OperationInProposalExistsException("EXCEPTION")
            lookup.update(foo="bar")
            self.assertTrue(lookup._retriggered)
            self.assertEqual(lookup._retriggered_kwargs.get("foo"), "bar")

    def test_retrigger_new(self):
        lookup = lookup_new_event()
        with mock.patch("bookied_sync.event.LookupEvent.propose_new") as m:
            m.side_effect = OperationInProposalExistsException("EXCEPTION")
            lookup.update(foo="bar")
            self.assertTrue(lookup._retriggered)
            self.assertEqual(lookup._retriggered_kwargs.get("foo"), "bar")
