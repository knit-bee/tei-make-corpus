import contextlib
import io
import os
import sys
import unittest

from lxml import etree

from tei_make_corpus.cli.make_corpus_usecase import CliRequest, TeiMakeCorpusUseCaseImpl
from tei_make_corpus.corpus_stream import CorpusStreamImpl


class IntegrationTest(unittest.TestCase):
    def setUp(self):
        self.out_stream = CorpusStreamImpl()
        self.use_case = TeiMakeCorpusUseCaseImpl(self.out_stream)

    def tearDown(self):
        if self.out_stream.output_file and os.path.exists(self.out_stream.output_file):
            os.remove(self.out_stream.output_file)

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

    def test_element_with_non_ascii_text_removed_if_equal_in_common_header(self):
        request = CliRequest(
            header_file=os.path.join("tests", "testdata", "enc_corpus", "header.xml"),
            corpus_dir=os.path.join("tests", "testdata", "enc_corpus"),
            clean_header=True,
        )
        with contextlib.redirect_stdout(
            io.TextIOWrapper(io.BytesIO(), sys.stdout.encoding)
        ) as pseudo:
            self.use_case.process(request)
        pseudo.seek(0)
        output_tree = etree.parse(pseudo)
        result = output_tree.findall(".//{*}address")
        self.assertEqual(len(result), 1)

    def test_output_written_to_file_if_enabled(self):
        output_file = os.path.join("tests", "testdata", "output.xml")
        request = CliRequest(
            header_file=os.path.join("tests", "testdata", "header.xml"),
            corpus_dir=os.path.join("tests", "testdata", "rec_corpus"),
            output_file=output_file,
        )
        self.use_case.process(request)
        output_tree = etree.parse(output_file)
        result = output_tree.getroot().getchildren()
        self.assertEqual(len(result), 5)
