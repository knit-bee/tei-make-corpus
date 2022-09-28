import os
import tempfile
import unittest

from lxml import etree

from tei_make_corpus.corpus_maker import TeiCorpusMaker
from tests.utils import create_validator


class TeiCorpusMakerTester(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = create_validator(
            os.path.join("tests", "testdata", "tei_all.rng")
        )

    def setUp(self):
        self.corpus_maker = TeiCorpusMaker()
        self.output_file = os.path.join("tests", "testdata", "output_file.xml")

    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_xml_declaration_written_to_corpus_file(self):
        header_file = os.path.join("tests", "testdata", "header.xml")
        empty_dir = os.path.join("tests", "testdata", "empty")
        with tempfile.TemporaryDirectory() as tempdir:
            _, output_file = tempfile.mkstemp(".xml", dir=tempdir, text=True)
            self.corpus_maker.build_corpus(empty_dir, header_file, output_file)
            with open(output_file) as ptr:
                file_content = ptr.read()
        xml_declaration = "<?xml version='1.0' encoding='utf-8'?>"
        self.assertTrue(xml_declaration in file_content)

    def test_data_from_header_file_written_to_corpus_file(self):
        header_file = os.path.join("tests", "testdata", "header.xml")
        empty_dir = os.path.join("tests", "testdata", "empty")
        with tempfile.TemporaryDirectory() as tempdir:
            _, output_file = tempfile.mkstemp(".xml", dir=tempdir, text=True)
            self.corpus_maker.build_corpus(empty_dir, header_file, output_file)
            with open(output_file) as ptr:
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
        corpus_files = self.corpus_maker._get_paths_for_corpus_files(
            corpus_dir, header_file
        )
        expected = [
            "tests/testdata/corpus/file1.xml",
            "tests/testdata/corpus/file2.xml",
        ]
        self.assertEqual(sorted(list(corpus_files)), expected)

    def test_non_xml_files_ignored_in_corpus_directory(self):
        corpus_dir = os.path.join("tests", "testdata", "corpus")
        header_file = "header.xml"
        corpus_files = self.corpus_maker._get_paths_for_corpus_files(
            corpus_dir, header_file
        )
        expected = [
            "tests/testdata/corpus/file1.xml",
            "tests/testdata/corpus/file2.xml",
        ]
        self.assertEqual(sorted(list(corpus_files)), expected)

    def test_corpus_files_found_recursively(self):
        corpus_dir = os.path.join("tests", "testdata", "rec_corpus")
        header_file = "header.xml"
        corpus_files = self.corpus_maker._get_paths_for_corpus_files(
            corpus_dir, header_file
        )
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
        self.corpus_maker.build_corpus(corpus_dir, header_file, self.output_file)
        doc = etree.parse(self.output_file)
        tei_nodes = doc.findall(
            ".//TEI", namespaces={None: "http://www.tei-c.org/ns/1.0"}
        )
        self.assertEqual(len(tei_nodes), 4)

    def test_resulting_file_is_valid_tei(self):
        corpus_dir = os.path.join("tests", "testdata", "rec_corpus")
        header_file = os.path.join("tests", "testdata", "header.xml")
        self.corpus_maker.build_corpus(corpus_dir, header_file, self.output_file)
        doc = etree.parse(self.output_file)
        result = self.validator.validate(doc)
        self.assertTrue(result)
