import os
import random
import unittest

from tei_make_corpus.cli.corpus_config import CorpusConfig
from tei_make_corpus.partitioner import Partitioner
from tests.utils import MockHeaderHandler


class MockPathFinder:
    def __init__(self):
        self.files = dict()

    def get_paths_for_corpus_files(self, corpus_dir, header_file):
        return self.files.get(corpus_dir, [])


class PartitionerTest(unittest.TestCase):
    def setUp(self):
        self.mock_header_handler = MockHeaderHandler()
        self.mock_path_finder = MockPathFinder()
        self.partitioner = Partitioner(self.mock_header_handler, self.mock_path_finder)
        self.header_file = "header.xml"

    def test_only_one_partition_returned_in_default_setting(self):
        corpus_dir = os.path.join("tests", "testdata", "rec_corpus")
        header_file = os.path.join("tests", "testdata", "header.xml")
        corpus_files = [
            os.path.join(root, file)
            for root, dirs, files in os.walk(corpus_dir)
            for file in files
        ]
        self.mock_path_finder.files[corpus_dir] = corpus_files
        result = list(self.partitioner.get_partitions(corpus_dir, header_file))
        self.assertEqual(len(result), 1)

    def test_partitioning_with_number_of_documents_per_file(self):
        total_no_files = 1000
        split_val = 100
        corpus_files = ["file.xml"] * total_no_files
        self.mock_path_finder.files["test_dir"] = corpus_files
        config = CorpusConfig(clean_header=False, split_docs=split_val)
        partitions = list(
            self.partitioner.get_partitions("test_dir", self.header_file, config)
        )
        self.assertEqual(len(partitions), 10)
        self.assertEqual(sum(len(part) for part in partitions), total_no_files)

    def test_partitioning_with_random_number_of_documents_per_file(self):
        total_no_files = random.randint(10, 15_000_000)
        split_val = random.randint(1, total_no_files)
        corpus_dir = "test_dir"
        corpus_files = [f"file{i}.xml" for i in range(total_no_files)]
        config = CorpusConfig(clean_header=False, split_docs=split_val)
        self.mock_path_finder.files[corpus_dir] = corpus_files
        partitions = self.partitioner.get_partitions(
            corpus_dir, self.header_file, config
        )
        self.assertEqual(sum(len(part) for part in partitions), total_no_files)

    def test_partitioning_split_value_larger_than_total_returns_one_partition(self):
        total_no_files = random.randint(10, 15_000)
        split_val = random.randint(total_no_files, 15_000_000)
        corpus_dir = "test_dir"
        corpus_files = [f"file{i}.xml" for i in range(total_no_files)]
        self.mock_path_finder.files[corpus_dir] = corpus_files
        config = CorpusConfig(clean_header=False, split_docs=split_val)
        partitions = list(
            self.partitioner.get_partitions(corpus_dir, self.header_file, config)
        )
        self.assertEqual(len(partitions), 1)

    def test_all_files_contained_in_partitions(self):
        total_no_files = random.randint(100, 10_000)
        split_val = random.randint(10, total_no_files)
        corpus_dir = "corpus"
        corpus_files = [f"file{i}.xml" for i in range(total_no_files)]
        self.mock_path_finder.files[corpus_dir] = corpus_files
        config = CorpusConfig(clean_header=False, split_docs=split_val)
        partitions = self.partitioner.get_partitions(
            corpus_dir, self.header_file, config
        )
        result = []
        for part in partitions:
            result += part.files
        self.assertEqual(result, corpus_files)

    def test_last_partition_with_only_small_amount_of_file_avoided(self):
        total_no_files = 1001
        split_val = 100
        corpus_dir = "corpus"
        corpus_files = ["file.xml"] * total_no_files
        self.mock_path_finder.files[corpus_dir] = corpus_files
        config = CorpusConfig(clean_header=False, split_docs=split_val)
        partitions = list(
            self.partitioner.get_partitions(corpus_dir, self.header_file, config)
        )
        last_partition = partitions[-1]
        self.assertTrue(len(last_partition) > 1)

    def test_last_partition_contains_at_least_thirty_percent_of_intended_chunk_size(
        self,
    ):
        split_val = 100
        for num_files in range(1001, 1030):
            corpus_dir = "corpus"
            corpus_files = ["file.xml"] * num_files
            self.mock_path_finder.files[corpus_dir] = corpus_files
            config = CorpusConfig(clean_header=False, split_docs=split_val)
            partitions = list(
                self.partitioner.get_partitions(corpus_dir, self.header_file, config)
            )
            last_partition = partitions[-1]
            with self.subTest():
                self.assertTrue(len(last_partition) > split_val * 0.3)
