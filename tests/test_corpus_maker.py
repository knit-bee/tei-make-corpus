import os
import unittest

from lxml import etree

from tei_make_corpus.corpus_maker import TeiCorpusMaker
from tei_make_corpus.header_handler import TeiHeaderHandlerImpl
from tests.utils import create_validator


class MockCorpusStream:
    file = os.path.join("tests", "testdata", "output_file.xml")

    def path(self):
        return self.file


class MockHeaderHandler:
    def common_header(self):
        return None

    def declutter_individual_header(self, iheader):
        pass


class TeiCorpusMakerTester(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = create_validator(
            os.path.join("tests", "testdata", "tei_all.rng")
        )

    def setUp(self):
        self.mock_stream = MockCorpusStream()
        self.mock_header_handler = MockHeaderHandler()

    def tearDown(self):
        if os.path.exists(self.mock_stream.file):
            os.remove(self.mock_stream.file)

    def test_xml_declaration_written_to_corpus_file(self):
        header_file = os.path.join("tests", "testdata", "header.xml")
        empty_dir = os.path.join("tests", "testdata", "empty")
        header_handler = TeiHeaderHandlerImpl(header_file)
        corpus_maker = TeiCorpusMaker(self.mock_stream, header_handler)
        corpus_maker.build_corpus(empty_dir, header_file)
        with open(self.mock_stream.file) as ptr:
            file_content = ptr.read()
        xml_declaration = "<?xml version='1.0' encoding='utf-8'?>"
        self.assertTrue(xml_declaration in file_content)

    def test_data_from_header_file_written_to_corpus_file(self):
        header_file = os.path.join("tests", "testdata", "header.xml")
        empty_dir = os.path.join("tests", "testdata", "empty")
        header_handler = TeiHeaderHandlerImpl(header_file)
        corpus_maker = TeiCorpusMaker(self.mock_stream, header_handler)
        corpus_maker.build_corpus(empty_dir, header_file)
        with open(self.mock_stream.file) as ptr:
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

    def test_header_file_ignored_if_in_corpus_directory(self):
        corpus_dir = os.path.join("tests", "testdata", "corpus")
        header_file = "header.xml"
        corpus_maker = TeiCorpusMaker(self.mock_stream, self.mock_header_handler)
        corpus_files = corpus_maker._get_paths_for_corpus_files(corpus_dir, header_file)
        expected = [
            "tests/testdata/corpus/file1.xml",
            "tests/testdata/corpus/file2.xml",
        ]
        self.assertEqual(sorted(list(corpus_files)), expected)

    def test_header_file_ignored_if_in_corpus_directory_with_path(self):
        corpus_dir = os.path.join("tests", "testdata", "corpus")
        header_file = os.path.join("tests", "testdata", "corpus", "header.xml")
        corpus_maker = TeiCorpusMaker(self.mock_stream, self.mock_header_handler)
        corpus_files = corpus_maker._get_paths_for_corpus_files(corpus_dir, header_file)
        expected = [
            "tests/testdata/corpus/file1.xml",
            "tests/testdata/corpus/file2.xml",
        ]
        self.assertEqual(sorted(list(corpus_files)), expected)

    def test_non_xml_files_ignored_in_corpus_directory(self):
        corpus_dir = os.path.join("tests", "testdata", "corpus")
        header_file = "header.xml"
        corpus_maker = TeiCorpusMaker(self.mock_stream, self.mock_header_handler)
        corpus_files = corpus_maker._get_paths_for_corpus_files(corpus_dir, header_file)
        expected = [
            "tests/testdata/corpus/file1.xml",
            "tests/testdata/corpus/file2.xml",
        ]
        self.assertEqual(sorted(list(corpus_files)), expected)

    def test_corpus_files_found_recursively(self):
        corpus_dir = os.path.join("tests", "testdata", "rec_corpus")
        header_file = "header.xml"
        corpus_maker = TeiCorpusMaker(self.mock_stream, self.mock_header_handler)
        corpus_files = corpus_maker._get_paths_for_corpus_files(corpus_dir, header_file)
        expected = [
            "tests/testdata/rec_corpus/part1/subpart/file1.xml",
            "tests/testdata/rec_corpus/part1/subpart/file2.xml",
            "tests/testdata/rec_corpus/part2/subpart/file21.xml",
            "tests/testdata/rec_corpus/part2/subpart/file22.xml",
        ]
        self.assertEqual(sorted(list(corpus_files)), expected)

    def test_all_corpus_files_added_to_output_doc(self):
        corpus_dir = os.path.join("tests", "testdata", "rec_corpus")
        header_file = os.path.join("tests", "testdata", "header.xml")
        header_handler = TeiHeaderHandlerImpl(header_file)
        corpus_maker = TeiCorpusMaker(self.mock_stream, header_handler)
        corpus_maker.build_corpus(corpus_dir, header_file)
        doc = etree.parse(self.mock_stream.file)
        tei_nodes = doc.findall(
            ".//TEI", namespaces={None: "http://www.tei-c.org/ns/1.0"}
        )
        self.assertEqual(len(tei_nodes), 4)

    def test_resulting_file_is_valid_tei(self):
        corpus_dir = os.path.join("tests", "testdata", "rec_corpus")
        header_file = os.path.join("tests", "testdata", "header.xml")
        header_handler = TeiHeaderHandlerImpl(header_file)
        corpus_maker = TeiCorpusMaker(self.mock_stream, header_handler)
        corpus_maker.build_corpus(corpus_dir, header_file)
        doc = etree.parse(self.mock_stream.file)
        result = self.validator.validate(doc)
        self.assertTrue(result)

    def test_non_tei_xml_files_omitted(self):
        corpus_dir = os.path.join("tests", "testdata", "contaminated")
        header_file = os.path.join("tests", "testdata", "header.xml")
        header_handler = TeiHeaderHandlerImpl(header_file)
        corpus_maker = TeiCorpusMaker(self.mock_stream, header_handler)
        corpus_maker.build_corpus(corpus_dir, header_file)
        tei_corpus_root = etree.parse(self.mock_stream.file).getroot()
        # teiCorpus should have 3 children
        self.assertEqual(len(tei_corpus_root), 3)

    def test_xmlid_attribute_removed(self):
        file = os.path.join("tests", "testdata", "corpus", "file1.xml")
        corpus_maker = TeiCorpusMaker(self.mock_stream, self.mock_header_handler)
        processed = corpus_maker._prepare_single_tei_file(file)
        result = processed.findall(".//*[@{http://www.w3.org/XML/1998/namespace}id]")
        self.assertEqual(result, [])

    def test_element_from_individual_header_removed_if_equal_in_common_header(self):
        corpus_dir = os.path.join("tests", "testdata", "corpus_header")
        header_file = os.path.join(corpus_dir, "header.xml")
        header_handler = TeiHeaderHandlerImpl(header_file)
        corpus_maker = TeiCorpusMaker(self.mock_stream, header_handler)
        corpus_maker.build_corpus(corpus_dir, header_file)
        doc = etree.parse(self.mock_stream.file)
        result = doc.findall(
            ".//funder", namespaces={None: "http://www.tei-c.org/ns/1.0"}
        )
        self.assertEqual(len(result), 1)

    def test_element_retained_if_content_is_different_from_common_header(self):
        corpus_dir = os.path.join("tests", "testdata", "corpus_header")
        header_file = os.path.join(corpus_dir, "header.xml")
        header_handler = TeiHeaderHandlerImpl(header_file)
        corpus_maker = TeiCorpusMaker(self.mock_stream, header_handler)
        corpus_maker.build_corpus(corpus_dir, header_file)
        doc = etree.parse(self.mock_stream.file)
        result = doc.findall(
            ".//author", namespaces={None: "http://www.tei-c.org/ns/1.0"}
        )
        self.assertEqual(len(result), 4)
