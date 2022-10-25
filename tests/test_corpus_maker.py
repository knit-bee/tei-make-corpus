import os
import unittest

from lxml import etree

from tei_make_corpus.cli.corpus_config import CorpusConfig
from tei_make_corpus.corpus_maker import TeiCorpusMaker
from tei_make_corpus.corpus_stream import CorpusStreamImpl
from tei_make_corpus.header_handler import TeiHeaderHandlerImpl
from tei_make_corpus.partitioner import Partitioner
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
        self.partitioner = Partitioner(self.header_handler)
        self.config_clean = CorpusConfig(clean_header=True)
        self.config_default = CorpusConfig(clean_header=False)

    def tearDown(self):
        if os.path.exists(self.mock_stream.output_file):
            os.remove(self.mock_stream.output_file)

    def test_xml_declaration_written_to_corpus_file(self):
        header_file = os.path.join("tests", "testdata", "header.xml")
        empty_dir = os.path.join("tests", "testdata", "empty")
        corpus_maker = TeiCorpusMaker(
            self.mock_stream, self.partitioner, self.config_default
        )
        corpus_maker.build_corpus(empty_dir, header_file)
        with open(self.mock_stream.output_file) as ptr:
            file_content = ptr.read()
        xml_declaration = "<?xml version='1.0' encoding='UTF-8'?>"
        self.assertTrue(xml_declaration in file_content)

    def test_data_from_header_file_written_to_corpus_file(self):
        header_file = os.path.join("tests", "testdata", "header.xml")
        empty_dir = os.path.join("tests", "testdata", "empty")
        header_handler = TeiHeaderHandlerImpl(header_file)
        partitioner = Partitioner(header_handler)
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
        partitioner = Partitioner(header_handler)
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
        partitioner = Partitioner(header_handler)
        corpus_maker = TeiCorpusMaker(
            self.mock_stream, partitioner, self.config_default
        )
        corpus_maker.build_corpus(corpus_dir, header_file)
        doc = etree.parse(self.mock_stream.output_file)
        result = self.validator.validate(doc)
        self.assertTrue(result)

    def test_non_tei_xml_files_omitted(self):
        corpus_dir = os.path.join("tests", "testdata", "contaminated")
        header_file = os.path.join("tests", "testdata", "header.xml")
        header_handler = TeiHeaderHandlerImpl(header_file)
        partitioner = Partitioner(header_handler)
        corpus_maker = TeiCorpusMaker(
            self.mock_stream, partitioner, self.config_default
        )
        corpus_maker.build_corpus(corpus_dir, header_file)
        tei_corpus_root = etree.parse(self.mock_stream.output_file).getroot()
        # teiCorpus should have 3 children
        self.assertEqual(len(tei_corpus_root), 3)

    def test_element_from_individual_header_removed_if_equal_in_common_header(self):
        corpus_dir = os.path.join("tests", "testdata", "corpus_header")
        header_file = os.path.join(corpus_dir, "header.xml")
        header_handler = TeiHeaderHandlerImpl(header_file)
        partitioner = Partitioner(header_handler)
        corpus_maker = TeiCorpusMaker(self.mock_stream, partitioner, self.config_clean)
        corpus_maker.build_corpus(corpus_dir, header_file)
        doc = etree.parse(self.mock_stream.output_file)
        result = doc.findall(
            ".//funder", namespaces={None: "http://www.tei-c.org/ns/1.0"}
        )
        self.assertEqual(len(result), 1)

    def test_element_retained_if_content_is_different_from_common_header(self):
        corpus_dir = os.path.join("tests", "testdata", "corpus_header")
        header_file = os.path.join(corpus_dir, "header.xml")
        header_handler = TeiHeaderHandlerImpl(header_file)
        partitioner = Partitioner(header_handler)
        corpus_maker = TeiCorpusMaker(self.mock_stream, partitioner, self.config_clean)
        corpus_maker.build_corpus(corpus_dir, header_file)
        doc = etree.parse(self.mock_stream.output_file)
        result = doc.findall(
            ".//author", namespaces={None: "http://www.tei-c.org/ns/1.0"}
        )
        self.assertEqual(len(result), 4)

    def test_individual_header_not_changed_if_option_is_set_to_false(self):
        corpus_dir = os.path.join("tests", "testdata", "corpus_header")
        header_file = os.path.join(corpus_dir, "header.xml")
        header_handler = TeiHeaderHandlerImpl(header_file)
        partitioner = Partitioner(header_handler)
        corpus_maker = TeiCorpusMaker(
            self.mock_stream, partitioner, self.config_default
        )
        corpus_maker.build_corpus(corpus_dir, header_file)
        doc = etree.parse(self.mock_stream.output_file)
        result = doc.findall(
            ".//funder", namespaces={None: "http://www.tei-c.org/ns/1.0"}
        )
        self.assertEqual(len(result), 2)
