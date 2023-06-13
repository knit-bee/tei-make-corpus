import os
import random
import unittest

from lxml import etree

from tei_make_corpus.cli.corpus_config import CorpusConfig
from tei_make_corpus.partitioner import Partitioner
from tei_make_corpus.xmlid_handler import XmlIdRemover
from tests.utils import MockHeaderHandler


class MockPathFinder:
    def __init__(self):
        self.files = dict()

    def get_paths_for_corpus_files(self, corpus_dir, header_file):
        return self.files.get(corpus_dir, [])


class MockSizeEstimator:
    def __init__(self):
        self.file_size = 1000

    def set_file_size(self, file_size):
        self.file_size = file_size

    def determine_file_sizes(self, list_of_file_paths):
        return [self.file_size for _ in range(len(list_of_file_paths))]


class PartitionerTest(unittest.TestCase):
    def setUp(self):
        self.mock_header_handler = MockHeaderHandler()
        self.mock_path_finder = MockPathFinder()
        self.size_estimator = MockSizeEstimator()
        self.id_handler = XmlIdRemover()
        self.partitioner = Partitioner(
            header_handler=self.mock_header_handler,
            path_finder=self.mock_path_finder,
            size_estimator=self.size_estimator,
            xmlid_handler=self.id_handler,
        )
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

    def test_partitioning_on_empty_directory_returns_empty_iterable(self):
        config = CorpusConfig(clean_header=False, split_docs=3)
        partitions = self.partitioner.get_partitions("empty", self.header_file, config)
        self.assertEqual(list(partitions), [])

    def test_partitioning_with_file_size(self):
        total_no_files = 100
        split_val = 10_000
        corpus_files = ["file.xml"] * total_no_files
        self.mock_path_finder.files["test_dir"] = corpus_files
        config = CorpusConfig(clean_header=False, split_size=split_val)
        partitions = list(
            self.partitioner.get_partitions("test_dir", self.header_file, config)
        )
        self.assertEqual(len(partitions), 10)
        self.assertEqual(sum(len(part) for part in partitions), total_no_files)

    def test_partitioning_with_random_file_size(self):
        total_no_files = random.randint(10, 15_000_000)
        split_val = random.randint(100_000, 1_000_000)
        self.size_estimator.set_file_size(random.randint(1000, 10_000))
        corpus_dir = "test_dir"
        corpus_files = [f"file{i}.xml" for i in range(total_no_files)]
        config = CorpusConfig(clean_header=False, split_size=split_val)
        self.mock_path_finder.files[corpus_dir] = corpus_files
        partitions = self.partitioner.get_partitions(
            corpus_dir, self.header_file, config
        )
        self.assertEqual(sum(len(part) for part in partitions), total_no_files)

    def test_partitioning_split_size_larger_than_total_returns_one_partition(self):
        total_no_files = random.randint(10, 15_000)
        split_val = random.randint(total_no_files * 1000, 15_000_000)
        corpus_dir = "test_dir"
        corpus_files = [f"file{i}.xml" for i in range(total_no_files)]
        self.mock_path_finder.files[corpus_dir] = corpus_files
        config = CorpusConfig(clean_header=False, split_size=split_val)
        partitions = list(
            self.partitioner.get_partitions(corpus_dir, self.header_file, config)
        )
        self.assertEqual(len(partitions), 1)

    def test_all_files_contained_in_partitions_with_split_size(self):
        total_no_files = random.randint(100, 10_000)
        split_val = 100_000
        self.size_estimator.set_file_size(random.randint(1000, 10_000))
        corpus_dir = "corpus"
        corpus_files = [f"file{i}.xml" for i in range(total_no_files)]
        self.mock_path_finder.files[corpus_dir] = corpus_files
        config = CorpusConfig(clean_header=False, split_size=split_val)
        partitions = self.partitioner.get_partitions(
            corpus_dir, self.header_file, config
        )
        result = []
        for part in partitions:
            result += part.files
        self.assertEqual(result, corpus_files)

    def test_each_partition_contains_intended_number_of_files(self):
        total_no_files = random.randint(1000, 1_000_000)
        split_val = random.randint(100, 10_000)
        corpus_dir = "corpus"
        corpus_files = [f"file{i}.xml" for i in range(total_no_files)]
        self.mock_path_finder.files[corpus_dir] = corpus_files
        config = CorpusConfig(clean_header=False, split_docs=split_val)
        partition_lengths = [
            len(partition)
            for partition in self.partitioner.get_partitions(
                corpus_dir, self.header_file, config
            )
        ]
        result = [
            part == split_val
            or part in range(int(split_val * 0.3), int(split_val * 1.3))
            for part in partition_lengths
        ]
        self.assertTrue(all(result))

    def test_all_but_last_partition_have_intended_size_at_least(self):
        total_no_files = random.randint(10, 15_000_000)
        split_val = random.randint(100_000, 1_000_000)
        single_file_size = random.randint(1000, 10_000)
        self.size_estimator.set_file_size(single_file_size)
        corpus_dir = "test_dir"
        corpus_files = [f"file{i}.xml" for i in range(total_no_files)]
        config = CorpusConfig(clean_header=False, split_size=split_val)
        self.mock_path_finder.files[corpus_dir] = corpus_files
        partitions = self.partitioner.get_partitions(
            corpus_dir, self.header_file, config
        )
        partition_sizes = [len(part) * single_file_size for part in partitions]
        self.assertTrue(
            all(
                size
                in range(
                    split_val - single_file_size,
                    split_val + single_file_size + 1,
                )
                for size in partition_sizes[:-1]
            )
        )

    def test_partitioning_on_empty_directory_returns_empty_iterable_file_size(self):
        config = CorpusConfig(clean_header=False, split_size=1000)
        partitions = self.partitioner.get_partitions("empty", self.header_file, config)
        self.assertEqual(list(partitions), [])

    def test_processing_instructions_passed_to_partition(self):
        pis = [etree.PI("test")]
        partitioner = Partitioner(
            self.mock_header_handler,
            self.mock_path_finder,
            self.size_estimator,
            self.id_handler,
            xml_processing_instructions=pis,
        )
        corpus_dir = os.path.join("tests", "testdata", "rec_corpus")
        header_file = os.path.join("tests", "testdata", "header.xml")
        corpus_files = [
            os.path.join(root, file)
            for root, dirs, files in os.walk(corpus_dir)
            for file in files
        ]
        self.mock_path_finder.files[corpus_dir] = corpus_files
        partition = next(partitioner.get_partitions(corpus_dir, header_file))
        result = [pi.target for pi in partition.xml_processing_instructions]
        self.assertEqual(result, ["test"])
