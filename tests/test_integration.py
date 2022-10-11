import contextlib
import io
import sys
import unittest
import os

from lxml import etree

from tei_make_corpus.cli.make_corpus_usecase import CliRequest, TeiMakeCorpusUseCaseImpl


class IntegrationTest(unittest.TestCase):
    def setUp(self):
        self.use_case = TeiMakeCorpusUseCaseImpl()

    def test_xml_element_tree_generated(self):
        request = CliRequest(
            header_file=os.path.join("tests", "testdata", "header.xml"),
            corpus_dir=os.path.join("tests", "testdata", "rec_corpus"),
        )
        with contextlib.redirect_stdout(
            io.TextIOWrapper(io.BytesIO(), sys.stdout.encoding)
        ) as pseudo:
            self.use_case.process(request)
        pseudo.seek(0)
        result = etree.parse(pseudo)
        self.assertTrue(isinstance(result, etree._ElementTree))

    def test_header_in_output(self):
        header_file = os.path.join("tests", "testdata", "header.xml")
        request = CliRequest(
            header_file=header_file,
            corpus_dir=os.path.join("tests", "testdata", "corpus"),
        )
        with contextlib.redirect_stdout(
            io.TextIOWrapper(io.BytesIO(), sys.stdout.encoding)
        ) as pseudo:
            self.use_case.process(request)
        pseudo.seek(0)
        output_tree = etree.parse(pseudo)
        result = output_tree.getroot()[0].tag
        self.assertEqual(result, "{http://www.tei-c.org/ns/1.0}teiHeader")

    def test_all_tei_files_added(self):
        request = CliRequest(
            header_file=os.path.join("tests", "testdata", "header.xml"),
            corpus_dir=os.path.join("tests", "testdata", "rec_corpus"),
        )
        with contextlib.redirect_stdout(
            io.TextIOWrapper(io.BytesIO(), sys.stdout.encoding)
        ) as pseudo:
            self.use_case.process(request)
        pseudo.seek(0)
        output_tree = etree.parse(pseudo)
        result = output_tree.getroot().getchildren()
        self.assertEqual(len(result), 5)
