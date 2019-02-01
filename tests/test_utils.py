import unittest
from bookied_sync import utils


class Testcases(unittest.TestCase):
    def test_dlist2dict(self):
        self.assertEqual(utils.dList2Dict([["a", "b"]]), dict(a="b"))

    def test_dict2dlist(self):
        self.assertEqual(utils.dict2dList(dict(a="b")), [["a", "b"]])
