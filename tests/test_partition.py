import os
import unittest

from tei_make_corpus.partition import Partition
from tests.utils import MockHeaderHandler


class PartitionTest(unittest.TestCase):
    def setUp(self):
        self.mock_header_handler = MockHeaderHandler()

    def test_xmlid_attribute_removed(self):
        file = os.path.join("tests", "testdata", "corpus", "file1.xml")
        partition = Partition(self.mock_header_handler, [])
        processed = partition._prepare_single_tei_file(file)
        result = processed.findall(".//*[@{http://www.w3.org/XML/1998/namespace}id]")
        self.assertEqual(result, [])
