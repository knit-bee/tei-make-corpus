import os
import tempfile
import unittest

from tei_make_corpus.path_finder import PathFinderImpl


class PathFinderTest(unittest.TestCase):
    def setUp(self):
        self.path_finder = PathFinderImpl()

    def test_header_file_ignored_if_in_corpus_directory(self):
        corpus_dir = os.path.join("tests", "testdata", "corpus")
        header_file = "header.xml"
        corpus_files = self.path_finder.get_paths_for_corpus_files(
            corpus_dir, header_file
        )
        expected = [
            "tests/testdata/corpus/file1.xml",
            "tests/testdata/corpus/file2.xml",
        ]
        self.assertEqual(list(corpus_files), expected)

    def test_header_file_ignored_if_in_corpus_directory_with_path(self):
        corpus_dir = os.path.join("tests", "testdata", "corpus")
        header_file = os.path.join("tests", "testdata", "corpus", "header.xml")
        corpus_files = self.path_finder.get_paths_for_corpus_files(
            corpus_dir, header_file
        )
        expected = [
            "tests/testdata/corpus/file1.xml",
            "tests/testdata/corpus/file2.xml",
        ]
        self.assertEqual(list(corpus_files), expected)

    def test_non_xml_files_ignored_in_corpus_directory(self):
        corpus_dir = os.path.join("tests", "testdata", "corpus")
        header_file = "header.xml"
        corpus_files = self.path_finder.get_paths_for_corpus_files(
            corpus_dir, header_file
        )
        expected = [
            "tests/testdata/corpus/file1.xml",
            "tests/testdata/corpus/file2.xml",
        ]
        self.assertEqual(list(corpus_files), expected)

    def test_corpus_files_found_recursively(self):
        corpus_dir = os.path.join("tests", "testdata", "rec_corpus")
        header_file = "header.xml"
        corpus_files = self.path_finder.get_paths_for_corpus_files(
            corpus_dir, header_file
        )
        expected = [
            "tests/testdata/rec_corpus/part1/subpart/file1.xml",
            "tests/testdata/rec_corpus/part1/subpart/file2.xml",
            "tests/testdata/rec_corpus/part2/subpart/file21.xml",
            "tests/testdata/rec_corpus/part2/subpart/file22.xml",
        ]
        self.assertEqual(list(corpus_files), expected)

    def test_files_ordered_alphabetically(self):
        header_file = "header.xml"
        with tempfile.TemporaryDirectory() as tempdir:
            file_names = []
            for _ in range(10):
                sub_dir = tempfile.mkdtemp(dir=tempdir)
                for _ in range(100):
                    _, tmp = tempfile.mkstemp(".xml", dir=sub_dir, text=True)
                    file_names.append(tmp)
            corpus_files = self.path_finder.get_paths_for_corpus_files(
                tempdir, header_file
            )
        self.assertEqual(corpus_files, sorted(file_names))
