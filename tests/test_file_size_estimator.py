import os
import unittest

from tei_make_corpus.file_size_estimator import FileSizeEstimatorImpl


class FileSizeEstimatorTest(unittest.TestCase):
    def setUp(self):
        self.size_estimator = FileSizeEstimatorImpl()

    def test_file_in_list_not_found(self):
        list_of_files = ["some_file.xml"]
        result = self.size_estimator.determine_file_sizes(list_of_files)
        self.assertEqual(result, [0])

    def test_file_sizes_returned_correctly(self):
        test_dir = os.path.join("tests", "testdata", "size")
        list_of_files = sorted(
            [os.path.join(test_dir, file) for file in os.listdir(test_dir)]
        )
        result = self.size_estimator.determine_file_sizes(list_of_files)
        expected = [12058, 6029, 3606, 2102, 498, 0]
        self.assertEqual(result, expected)

    def test_empty_list_passed(self):
        result = self.size_estimator.determine_file_sizes([])
        self.assertEqual(result, [])
