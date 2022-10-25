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
