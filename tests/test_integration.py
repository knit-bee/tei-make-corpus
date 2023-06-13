import contextlib
import io
import os
import re
import sys
import unittest

from lxml import etree

from tei_make_corpus.cli.make_corpus_usecase import CliRequest, TeiMakeCorpusUseCaseImpl
from tei_make_corpus.corpus_stream import CorpusStreamImpl


class IntegrationTest(unittest.TestCase):
    def setUp(self):
        self.out_stream = CorpusStreamImpl()
        self.use_case = TeiMakeCorpusUseCaseImpl(self.out_stream)
        self.test_dir = os.path.join("tests", "testdata")

    def tearDown(self):
        if self.out_stream.output_file and os.path.exists(self.out_stream.output_file):
            os.remove(self.out_stream.output_file)

    def test_xml_element_tree_generated(self):
        request = CliRequest(
            header_file=os.path.join(self.test_dir, "header.xml"),
            corpus_dir=os.path.join(self.test_dir, "rec_corpus"),
        )
        with contextlib.redirect_stdout(
            io.TextIOWrapper(io.BytesIO(), sys.stdout.encoding)
        ) as pseudo:
            self.use_case.process(request)
        pseudo.seek(0)
        result = etree.parse(pseudo)
        self.assertTrue(isinstance(result, etree._ElementTree))

    def test_header_in_output(self):
        header_file = os.path.join(self.test_dir, "header.xml")
        request = CliRequest(
            header_file=header_file,
            corpus_dir=os.path.join(self.test_dir, "corpus"),
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
            header_file=os.path.join(self.test_dir, "header.xml"),
            corpus_dir=os.path.join(self.test_dir, "rec_corpus"),
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
            header_file=os.path.join(self.test_dir, "enc_corpus", "header.xml"),
            corpus_dir=os.path.join(self.test_dir, "enc_corpus"),
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
        output_file = os.path.join(self.test_dir, "output.xml")
        request = CliRequest(
            header_file=os.path.join(self.test_dir, "header.xml"),
            corpus_dir=os.path.join(self.test_dir, "rec_corpus"),
            output_file=output_file,
        )
        self.use_case.process(request)
        output_tree = etree.parse(output_file)
        result = output_tree.getroot().getchildren()
        self.assertEqual(len(result), 5)

    def test_one_file_created_if_split_docs_is_set_to_10(self):
        request = CliRequest(
            header_file=os.path.join(self.test_dir, "header.xml"),
            corpus_dir=os.path.join(self.test_dir, "rec_corpus"),
            output_file=os.path.join(self.test_dir, "only_out.xml"),
            split_docs=10,
        )
        self.use_case.process(request)
        result = [
            file for file in os.listdir(self.test_dir) if file.startswith("only_out")
        ]
        self.assertEqual(len(result), 1)

    def test_multiple_files_created_with_split_docs_option(self):
        request = CliRequest(
            header_file=os.path.join(self.test_dir, "header.xml"),
            corpus_dir=os.path.join(self.test_dir, "rec_corpus"),
            output_file=os.path.join(self.test_dir, "part_out.xml"),
            split_docs=1,
        )
        self.use_case.process(request)
        result = [
            file for file in os.listdir(self.test_dir) if file.startswith("part_out")
        ]
        self.assertEqual(len(result), 4)
        self._remove_output_files(pattern=r"part_out\d*\.xml")

    def test_cleaning_of_header_performed_on_all_docs_with_split_docs(self):
        request = CliRequest(
            header_file=os.path.join(self.test_dir, "header2.xml"),
            corpus_dir=os.path.join(self.test_dir, "rec_corpus"),
            output_file=os.path.join(self.test_dir, "part_out.xml"),
            split_docs=2,
            clean_header=True,
        )
        self.use_case.process(request)
        output_files = [
            file for file in os.listdir(self.test_dir) if file.startswith("part_out")
        ]
        for file in output_files:
            doc = etree.parse(os.path.join(self.test_dir, file))
            with self.subTest():
                # encodingDesc should be removed from individual headers
                # bc it is same in common header
                self.assertEqual(len(doc.findall(".//{*}encodingDesc")), 1)
        self._remove_output_files(pattern=r"part_out\d*\.xml")

    def test_split_docs_option_without_output_file_uses_default_template_name(self):
        request = CliRequest(
            header_file=os.path.join(self.test_dir, "header.xml"),
            corpus_dir=os.path.join(self.test_dir, "rec_corpus"),
            split_docs=2,
        )
        self.use_case.process(request)
        self.assertTrue(self.out_stream.path().startswith("part"))
        self._remove_output_files(dir=os.getcwd(), pattern=r"part\d*\.xml")

    def test_one_file_created_if_intended_file_size_larger_than_total(self):
        request = CliRequest(
            header_file=os.path.join(self.test_dir, "header.xml"),
            corpus_dir=os.path.join(self.test_dir, "rec_corpus"),
            output_file=os.path.join(self.test_dir, "only_out.xml"),
            split_size=100000,
        )
        self.use_case.process(request)
        result = [
            file for file in os.listdir(self.test_dir) if file.startswith("only_out")
        ]
        self.assertEqual(len(result), 1)

    def test_multiple_files_created_with_split_size_option(self):
        request = CliRequest(
            header_file=os.path.join(self.test_dir, "header.xml"),
            corpus_dir=os.path.join(self.test_dir, "rec_corpus"),
            output_file=os.path.join(self.test_dir, "part_out.xml"),
            split_size=1000,
        )
        self.use_case.process(request)
        result = [
            file for file in os.listdir(self.test_dir) if file.startswith("part_out")
        ]
        self.assertEqual(len(result), 4)
        self._remove_output_files(pattern=r"part_out\d*\.xml")

    def test_cleaning_of_header_performed_on_all_docs_with_split_size(self):
        request = CliRequest(
            header_file=os.path.join(self.test_dir, "header2.xml"),
            corpus_dir=os.path.join(self.test_dir, "rec_corpus"),
            output_file=os.path.join(self.test_dir, "part_out.xml"),
            split_size=2000,
            clean_header=True,
        )
        self.use_case.process(request)
        output_files = [
            file for file in os.listdir(self.test_dir) if file.startswith("part_out")
        ]
        for file in output_files:
            doc = etree.parse(os.path.join(self.test_dir, file))
            with self.subTest():
                # encodingDesc should be removed from individual headers
                # bc it is same in common header
                self.assertEqual(len(doc.findall(".//{*}encodingDesc")), 1)
        self._remove_output_files(pattern=r"part_out\d*\.xml")

    def test_split_size_option_without_output_file_uses_default_template_name(self):
        request = CliRequest(
            header_file=os.path.join(self.test_dir, "header.xml"),
            corpus_dir=os.path.join(self.test_dir, "rec_corpus"),
            split_size=2000,
        )
        self.use_case.process(request)
        self.assertTrue(self.out_stream.path().startswith("part"))
        self._remove_output_files(dir=os.getcwd(), pattern=r"part\d*\.xml")

    def test_prefix_added_to_xmlid_attributes(self):
        request = CliRequest(
            header_file=os.path.join(self.test_dir, "xmlid", "header.xml"),
            corpus_dir=os.path.join(self.test_dir, "xmlid"),
            prefix_xmlid=True,
        )
        with contextlib.redirect_stdout(
            io.TextIOWrapper(io.BytesIO(), sys.stdout.encoding)
        ) as pseudo:
            self.use_case.process(request)
        pseudo.seek(0)
        doc = etree.parse(pseudo)
        result = [attr_val for attr_val in doc.xpath("//@xml:id | //@corresp")]
        expected = [
            "Funder",
            "#Publisher",
            "Publisher",
            "aq",
            "b",
            "blue",
            "c",
            "et",
            "et2",
            "et3",
            "f",
            "fr",
            "g",
            "i",
            "in",
            "k",
            "larger",
            "red",
            "right",
            "s",
            "smaller",
            "sub",
            "sup",
            "u",
            "uu",
            "p2b85cc-Funder",
            "#p2b85cc-Publisher",
            "p2b85cc-Publisher",
            "p2b85cc-aq",
            "p2b85cc-b",
            "p2b85cc-blue",
            "p2b85cc-c",
            "p2b85cc-et",
            "p2b85cc-et2",
            "p2b85cc-et3",
            "p2b85cc-f",
            "p2b85cc-fr",
            "p2b85cc-g",
            "p2b85cc-i",
            "p2b85cc-in",
            "p2b85cc-k",
            "p2b85cc-larger",
            "p2b85cc-red",
            "p2b85cc-right",
            "p2b85cc-s",
            "p2b85cc-smaller",
            "p2b85cc-sub",
            "p2b85cc-sup",
            "p2b85cc-u",
            "p2b85cc-uu",
            "p7556d0-Funder",
            "#p7556d0-Publisher",
            "p7556d0-Publisher",
            "p7556d0-aq",
            "p7556d0-b",
            "p7556d0-blue",
            "p7556d0-c",
            "p7556d0-et",
            "p7556d0-et2",
            "p7556d0-et3",
            "p7556d0-f",
            "p7556d0-fr",
            "p7556d0-g",
            "p7556d0-i",
            "p7556d0-in",
            "p7556d0-k",
            "p7556d0-larger",
            "p7556d0-red",
            "p7556d0-right",
            "p7556d0-s",
            "p7556d0-smaller",
            "p7556d0-sub",
            "p7556d0-sup",
            "p7556d0-u",
            "p7556d0-uu",
        ]
        self.assertEqual(result, expected)

    def test_prefix_added_to_xmlid_attributes_that_are_not_duplicates_in_common_header(
        self,
    ):
        request = CliRequest(
            header_file=os.path.join(self.test_dir, "xmlid", "header.xml"),
            corpus_dir=os.path.join(self.test_dir, "xmlid"),
            clean_header=True,
            prefix_xmlid=True,
        )
        with contextlib.redirect_stdout(
            io.TextIOWrapper(io.BytesIO(), sys.stdout.encoding)
        ) as pseudo:
            self.use_case.process(request)
        pseudo.seek(0)
        doc = etree.parse(pseudo)
        result = [
            attrib
            for attrib in doc.xpath(
                "tei:TEI//@xml:id", namespaces={"tei": "http://www.tei-c.org/ns/1.0"}
            )
        ]
        expected = [
            "p2b85cc-Publisher",
            "p7556d0-Publisher",
        ]
        self.assertEqual(result, expected)

    def test_processing_instructions_added_to_file(self):
        request = CliRequest(
            header_file=os.path.join(self.test_dir, "header.xml"),
            corpus_dir=os.path.join(self.test_dir, "corpus"),
            pis={"xml-model": "some text"},
        )
        with contextlib.redirect_stdout(
            io.TextIOWrapper(io.BytesIO(), sys.stdout.encoding)
        ) as pseudo:
            self.use_case.process(request)
        pseudo.seek(0)
        doc = etree.parse(pseudo)
        result = [node.target for node in doc.xpath("preceding-sibling::node()")]
        self.assertEqual(result, ["xml-model"])

    def _remove_output_files(self, dir=None, pattern=None):
        dir = dir or self.test_dir
        other_files = [file for file in os.listdir(dir) if re.match(pattern, file)]
        for file in other_files:
            os.remove(os.path.join(dir, file))
