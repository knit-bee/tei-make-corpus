import os
import unittest

from lxml import etree

from tei_make_corpus.cli.corpus_config import CorpusConfig
from tei_make_corpus.corpus_maker import TeiCorpusMaker
from tei_make_corpus.corpus_stream import CorpusStreamImpl
from tei_make_corpus.file_size_estimator import FileSizeEstimatorImpl
from tei_make_corpus.header_handler import TeiHeaderHandlerImpl
from tei_make_corpus.partitioner import Partitioner
from tei_make_corpus.path_finder import PathFinderImpl
from tei_make_corpus.xmlid_handler import XmlIdHandlerImpl
from tests.utils import MockHeaderHandler, create_validator


class TeiCorpusMakerTester(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = create_validator(
            os.path.join("tests", "testdata", "tei_all.rng")
        )

    def setUp(self):
        self.mock_stream = CorpusStreamImpl(
            os.path.join("tests", "testdata", "output_file.xml")
        )
        self.header_handler = MockHeaderHandler()
        self.path_finder = PathFinderImpl()
        self.size_estimator = FileSizeEstimatorImpl()
        self.xmlid_handler = XmlIdHandlerImpl()
        self.config_clean = CorpusConfig(clean_header=True)
        self.config_default = CorpusConfig(clean_header=False)
        self.partition_files = [
            "output_file0001.xml",
            "output_file0002.xml",
            "output_file0003.xml",
            "output_file0004.xml",
        ]

    def tearDown(self):
        if os.path.exists(self.mock_stream.output_file):
            os.remove(self.mock_stream.output_file)
        for file in self.partition_files:
            file_path = os.path.join("tests", "testdata", file)
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_data_from_header_file_written_to_corpus_file(self):
        header_file = os.path.join("tests", "testdata", "header.xml")
        empty_dir = os.path.join("tests", "testdata", "corpus")
        header_handler = TeiHeaderHandlerImpl(header_file)
        partitioner = Partitioner(
            header_handler, self.path_finder, self.size_estimator, self.xmlid_handler
        )
        corpus_maker = TeiCorpusMaker(
            self.mock_stream, partitioner, self.config_default
        )
        corpus_maker.build_corpus(empty_dir, header_file)
        with open(self.mock_stream.output_file) as ptr:
            file_content = ptr.read()
        self.assertTrue(
            """<teiHeader>
    <fileDesc>
        <titleStmt>
            <title/>
        </titleStmt>
        <publicationStmt>
          <p/>
        </publicationStmt>
        <sourceDesc>
          <p/>
        </sourceDesc>
    </fileDesc>
</teiHeader>"""
            in file_content
        )

    def test_all_corpus_files_added_to_output_doc(self):
        corpus_dir = os.path.join("tests", "testdata", "rec_corpus")
        header_file = os.path.join("tests", "testdata", "header.xml")
        header_handler = TeiHeaderHandlerImpl(header_file)
        partitioner = Partitioner(
            header_handler, self.path_finder, self.size_estimator, self.xmlid_handler
        )
        corpus_maker = TeiCorpusMaker(
            self.mock_stream, partitioner, self.config_default
        )
        corpus_maker.build_corpus(corpus_dir, header_file)
        doc = etree.parse(self.mock_stream.output_file)
        tei_nodes = doc.findall(
            ".//TEI", namespaces={None: "http://www.tei-c.org/ns/1.0"}
        )
        self.assertEqual(len(tei_nodes), 4)

    def test_resulting_file_is_valid_tei(self):
        corpus_dir = os.path.join("tests", "testdata", "rec_corpus")
        header_file = os.path.join("tests", "testdata", "header.xml")
        header_handler = TeiHeaderHandlerImpl(header_file)
        partitioner = Partitioner(
            header_handler, self.path_finder, self.size_estimator, self.xmlid_handler
        )
        corpus_maker = TeiCorpusMaker(
            self.mock_stream, partitioner, self.config_default
        )
        corpus_maker.build_corpus(corpus_dir, header_file)
        doc = etree.parse(self.mock_stream.output_file)
        result = self.validator.validate(doc)
        self.assertTrue(result)

    def test_only_one_file_created_if_partition_option_not_used(self):
        assert os.path.exists(self.mock_stream.path()) is False
        header_file = os.path.join("tests", "testdata", "header.xml")
        corpus_dir = os.path.join("tests", "testdata", "rec_corpus")
        header_handler = TeiHeaderHandlerImpl(header_file)
        partitioner = Partitioner(
            header_handler, self.path_finder, self.size_estimator, self.xmlid_handler
        )
        corpus_maker = TeiCorpusMaker(
            self.mock_stream, partitioner, self.config_default
        )
        corpus_maker.build_corpus(corpus_dir, header_file)
        self.assertTrue(os.path.exists(self.mock_stream.path()))

    def test_partition_output_multiple_files_created(self):
        header_file = os.path.join("tests", "testdata", "header.xml")
        corpus_dir = os.path.join("tests", "testdata", "rec_corpus")
        config = CorpusConfig(clean_header=False, split_docs=1)
        header_handler = TeiHeaderHandlerImpl(header_file)
        partitioner = Partitioner(
            header_handler, self.path_finder, self.size_estimator, self.xmlid_handler
        )
        stream = CorpusStreamImpl(os.path.join("tests", "testdata", "output_file.xml"))
        corpus_maker = TeiCorpusMaker(stream, partitioner, config)
        corpus_maker.build_corpus(corpus_dir, header_file)
        output_dir_content = os.listdir(os.path.join("tests", "testdata"))
        self.assertTrue(
            all(file in output_dir_content for file in self.partition_files)
        )

    def test_single_files_is_valid_if_corpus_is_partitioned(self):
        header_file = os.path.join("tests", "testdata", "header.xml")
        corpus_dir = os.path.join("tests", "testdata", "rec_corpus")
        config = CorpusConfig(clean_header=False, split_docs=1)
        header_handler = TeiHeaderHandlerImpl(header_file)
        partitioner = Partitioner(
            header_handler, self.path_finder, self.size_estimator, self.xmlid_handler
        )
        stream = CorpusStreamImpl(os.path.join("tests", "testdata", "output_file.xml"))
        corpus_maker = TeiCorpusMaker(stream, partitioner, config)
        corpus_maker.build_corpus(corpus_dir, header_file)
        for file in self.partition_files:
            file_path = os.path.join("tests", "testdata", file)
            doc = etree.parse(file_path)
            result = self.validator.validate(doc)
            with self.subTest():
                self.assertTrue(result)

    def test_common_header_written_to_all_files_if_partitioned(self):
        header_file = os.path.join("tests", "testdata", "header.xml")
        corpus_dir = os.path.join("tests", "testdata", "rec_corpus")
        config = CorpusConfig(clean_header=False, split_docs=1)
        header_handler = TeiHeaderHandlerImpl(header_file)
        partitioner = Partitioner(
            header_handler, self.path_finder, self.size_estimator, self.xmlid_handler
        )
        stream = CorpusStreamImpl(os.path.join("tests", "testdata", "output_file.xml"))
        corpus_maker = TeiCorpusMaker(stream, partitioner, config)
        corpus_maker.build_corpus(corpus_dir, header_file)
        for file in self.partition_files:
            file_path = os.path.join("tests", "testdata", file)
            doc = etree.parse(file_path)
            with self.subTest():
                self.assertEqual(len(doc.findall(".//{*}teiHeader")), 2)

    def test_no_output_file_created_if_corpus_dir_is_empty(self):
        header_file = os.path.join("tests", "testdata", "header.xml")
        empty_dir = os.path.join("tests", "testdata", "empty")
        header_handler = TeiHeaderHandlerImpl(header_file)
        partitioner = Partitioner(
            header_handler, self.path_finder, self.size_estimator, self.xmlid_handler
        )
        corpus_maker = TeiCorpusMaker(
            self.mock_stream, partitioner, self.config_default
        )
        corpus_maker.build_corpus(empty_dir, header_file)
        self.assertFalse(os.path.exists(self.mock_stream.path()))

    def test_partition_output_multiple_files_created_with_file_size(self):
        header_file = os.path.join("tests", "testdata", "header.xml")
        corpus_dir = os.path.join("tests", "testdata", "rec_corpus")
        config = CorpusConfig(clean_header=False, split_size=2000)
        header_handler = TeiHeaderHandlerImpl(header_file)
        partitioner = Partitioner(
            header_handler, self.path_finder, self.size_estimator, self.xmlid_handler
        )
        stream = CorpusStreamImpl(os.path.join("tests", "testdata", "output_file.xml"))
        corpus_maker = TeiCorpusMaker(stream, partitioner, config)
        corpus_maker.build_corpus(corpus_dir, header_file)
        output_dir_content = os.listdir(os.path.join("tests", "testdata"))
        self.assertTrue(
            all(file in output_dir_content for file in self.partition_files)
        )

    def test_single_files_is_valid_if_corpus_is_partitioned_with_file_size(self):
        header_file = os.path.join("tests", "testdata", "header.xml")
        corpus_dir = os.path.join("tests", "testdata", "rec_corpus")
        config = CorpusConfig(clean_header=False, split_size=2000)
        header_handler = TeiHeaderHandlerImpl(header_file)
        partitioner = Partitioner(
            header_handler, self.path_finder, self.size_estimator, self.xmlid_handler
        )
        stream = CorpusStreamImpl(os.path.join("tests", "testdata", "output_file.xml"))
        corpus_maker = TeiCorpusMaker(stream, partitioner, config)
        corpus_maker.build_corpus(corpus_dir, header_file)
        for file in self.partition_files:
            file_path = os.path.join("tests", "testdata", file)
            doc = etree.parse(file_path)
            result = self.validator.validate(doc)
            with self.subTest():
                self.assertTrue(result)

    def test_common_header_written_to_all_files_if_partitioned_with_file_size(self):
        header_file = os.path.join("tests", "testdata", "header.xml")
        corpus_dir = os.path.join("tests", "testdata", "rec_corpus")
        config = CorpusConfig(clean_header=False, split_size=2000)
        header_handler = TeiHeaderHandlerImpl(header_file)
        partitioner = Partitioner(
            header_handler, self.path_finder, self.size_estimator, self.xmlid_handler
        )
        stream = CorpusStreamImpl(os.path.join("tests", "testdata", "output_file.xml"))
        corpus_maker = TeiCorpusMaker(stream, partitioner, config)
        corpus_maker.build_corpus(corpus_dir, header_file)
        for file in self.partition_files:
            file_path = os.path.join("tests", "testdata", file)
            doc = etree.parse(file_path)
            with self.subTest():
                self.assertEqual(len(doc.findall(".//{*}teiHeader")), 2)

    def test_file_with_added_xmlid_prefixes_is_valid(self):
        corpus_dir = os.path.join("tests", "testdata", "xmlid")
        header_file = os.path.join(corpus_dir, "header.xml")
        header_handler = TeiHeaderHandlerImpl(header_file)
        partitioner = Partitioner(
            header_handler,
            self.path_finder,
            self.size_estimator,
            XmlIdHandlerImpl(
                action="prefix",
            ),
        )
        corpus_maker = TeiCorpusMaker(
            self.mock_stream, partitioner, self.config_default
        )
        corpus_maker.build_corpus(corpus_dir, header_file)
        doc = etree.parse(self.mock_stream.output_file)
        result = self.validator.validate(doc)
        self.assertTrue(result)

    def test_file_with_added_xmlid_prefixes_is_valid_header_cleaning(self):
        corpus_dir = os.path.join("tests", "testdata", "xmlid")
        header_file = os.path.join(corpus_dir, "header.xml")
        header_handler = TeiHeaderHandlerImpl(header_file)
        partitioner = Partitioner(
            header_handler,
            self.path_finder,
            self.size_estimator,
            XmlIdHandlerImpl(
                action="prefix",
            ),
        )
        corpus_maker = TeiCorpusMaker(self.mock_stream, partitioner, self.config_clean)
        corpus_maker.build_corpus(corpus_dir, header_file)
        doc = etree.parse(self.mock_stream.output_file)
        result = self.validator.validate(doc)
        self.assertTrue(result)
