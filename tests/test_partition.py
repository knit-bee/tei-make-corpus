import io
import os
import random
import unittest

from lxml import etree

from tei_make_corpus.header_handler import TeiHeaderHandlerImpl
from tei_make_corpus.partition import Partition
from tei_make_corpus.xmlid_handler import XmlIdPrefixer, XmlIdRemover
from tests.utils import MockHeaderHandler


class MockStream:
    def __init__(self):
        self.output_file = io.BytesIO()

    def path(self):
        return self.output_file


class MockDocIdHandler:
    def add_doc_id(self, doc_root, filepath):
        new = etree.Element("new")
        new.text = filepath
        doc_root.insert(0, new)


class PartitionTest(unittest.TestCase):
    def setUp(self):
        self.mock_header_handler = MockHeaderHandler()
        self.mock_stream = MockStream()
        self.xmlid_handler = XmlIdRemover()

    def test_xmlid_attribute_removed(self):
        file = os.path.join("tests", "testdata", "corpus", "file1.xml")
        partition = Partition(self.mock_header_handler, [], self.xmlid_handler)
        processed = partition._prepare_single_tei_file(file)
        result = processed.findall(".//*[@{http://www.w3.org/XML/1998/namespace}id]")
        self.assertEqual(result, [])

    def test_non_tei_xml_files_omitted(self):
        corpus_dir = os.path.join("tests", "testdata", "contaminated")
        header_file = os.path.join("tests", "testdata", "header.xml")
        header_handler = TeiHeaderHandlerImpl(header_file)
        corpus_files = [
            os.path.join(corpus_dir, file) for file in os.listdir(corpus_dir)
        ]
        partition = Partition(header_handler, corpus_files, self.xmlid_handler)
        partition.write_partition(self.mock_stream.path())
        self.mock_stream.output_file.seek(0)
        tei_corpus_root = etree.parse(self.mock_stream.output_file).getroot()
        # teiCorpus should have 3 children
        self.assertEqual(len(tei_corpus_root), 3)

    def test_element_from_individual_header_removed_if_equal_in_common_header(self):
        corpus_dir = os.path.join("tests", "testdata", "corpus_header")
        header_file = os.path.join(corpus_dir, "header.xml")
        corpus_files = [
            os.path.join(corpus_dir, file) for file in os.listdir(corpus_dir)
        ]
        header_handler = TeiHeaderHandlerImpl(header_file)
        partition = Partition(
            header_handler, corpus_files, self.xmlid_handler, clean_files=True
        )
        partition.write_partition(self.mock_stream.path())
        self.mock_stream.output_file.seek(0)
        doc = etree.parse(self.mock_stream.output_file)
        result = doc.findall(
            ".//funder", namespaces={None: "http://www.tei-c.org/ns/1.0"}
        )
        self.assertEqual(len(result), 1)

    def test_element_retained_if_content_is_different_from_common_header(self):
        corpus_dir = os.path.join("tests", "testdata", "corpus_header")
        header_file = os.path.join(corpus_dir, "header.xml")
        header_handler = TeiHeaderHandlerImpl(header_file)
        corpus_files = [
            os.path.join(corpus_dir, file) for file in os.listdir(corpus_dir)
        ]
        partition = Partition(
            header_handler, corpus_files, self.xmlid_handler, clean_files=True
        )
        partition.write_partition(self.mock_stream.path())
        self.mock_stream.output_file.seek(0)
        doc = etree.parse(self.mock_stream.output_file)
        result = doc.findall(
            ".//author", namespaces={None: "http://www.tei-c.org/ns/1.0"}
        )
        self.assertEqual(len(result), 4)

    def test_individual_header_not_changed_if_option_is_set_to_false(self):
        corpus_dir = os.path.join("tests", "testdata", "corpus_header")
        header_file = os.path.join(corpus_dir, "header.xml")
        corpus_files = [
            os.path.join(corpus_dir, file) for file in os.listdir(corpus_dir)
        ]
        header_handler = TeiHeaderHandlerImpl(header_file)
        partition = Partition(
            header_handler, corpus_files, self.xmlid_handler, clean_files=False
        )
        partition.write_partition(self.mock_stream.path())
        self.mock_stream.output_file.seek(0)
        doc = etree.parse(self.mock_stream.output_file)
        result = doc.findall(
            ".//funder", namespaces={None: "http://www.tei-c.org/ns/1.0"}
        )
        self.assertEqual(len(result), 2)

    def test_xml_declaration_written_to_corpus_file(self):
        partition = Partition(self.mock_header_handler, [], self.xmlid_handler)
        partition.write_partition(self.mock_stream.path())
        self.mock_stream.output_file.seek(0)
        file_content = self.mock_stream.output_file.read().decode("utf-8")
        xml_declaration = "<?xml version='1.0' encoding='UTF-8'?>"
        self.assertTrue(xml_declaration in file_content)

    def test_root_is_teiCorpus(self):
        corpus_dir = os.path.join("tests", "testdata", "corpus_header")
        header_file = os.path.join(corpus_dir, "header.xml")
        corpus_files = [
            os.path.join(corpus_dir, file)
            for file in os.listdir(corpus_dir)
            if file != "header.xml"
        ]
        header_handler = TeiHeaderHandlerImpl(header_file)
        partition = Partition(header_handler, corpus_files, self.xmlid_handler)
        partition.write_partition(self.mock_stream.path())
        self.mock_stream.output_file.seek(0)
        doc = etree.parse(self.mock_stream.output_file)
        result = doc.getroot().tag
        self.assertEqual(result, "{http://www.tei-c.org/ns/1.0}teiCorpus")

    def test_all_tei_files_from_partition_written_to_output(self):
        corpus_dir = os.path.join("tests", "testdata", "rec_corpus")
        header_file = os.path.join("tests", "testdata", "header.xml")
        corpus_files = [
            os.path.join(root, file)
            for root, dirs, files in os.walk(corpus_dir)
            for file in files
        ]
        header_handler = TeiHeaderHandlerImpl(header_file)
        partition = Partition(header_handler, corpus_files, self.xmlid_handler)
        partition.write_partition(self.mock_stream.path())
        self.mock_stream.output_file.seek(0)
        root = etree.parse(self.mock_stream.output_file).getroot()
        self.assertEqual(len(root), 5)

    def test_len_of_partition(self):
        expected = random.randint(1, 150_000_000)
        files = ["file"] * expected
        partition = Partition(self.mock_header_handler, files, self.xmlid_handler)
        self.assertEqual(len(partition), expected)

    def test_empty_file_in_corpus_ommited(self):
        corpus_dir = os.path.join("tests", "testdata", "dir_empty")
        header_file = os.path.join("tests", "testdata", "header.xml")
        header_handler = TeiHeaderHandlerImpl(header_file)
        corpus_files = [
            os.path.join(corpus_dir, file) for file in os.listdir(corpus_dir)
        ]
        partition = Partition(header_handler, corpus_files, self.xmlid_handler)
        partition.write_partition(self.mock_stream.path())
        self.mock_stream.output_file.seek(0)
        tei_corpus_root = etree.parse(self.mock_stream.output_file).getroot()
        self.assertEqual(len(tei_corpus_root), 3)

    def test_invalid_xml_file_in_corpus(self):
        corpus_dir = os.path.join("tests", "testdata", "dir_invalid")
        header_file = os.path.join("tests", "testdata", "header.xml")
        header_handler = TeiHeaderHandlerImpl(header_file)
        corpus_files = [
            os.path.join(corpus_dir, file) for file in os.listdir(corpus_dir)
        ]
        partition = Partition(header_handler, corpus_files, self.xmlid_handler)
        partition.write_partition(self.mock_stream.path())
        self.mock_stream.output_file.seek(0)
        tei_corpus_root = etree.parse(self.mock_stream.output_file).getroot()
        self.assertEqual(len(tei_corpus_root), 3)

    def test_filename_logged_on_parsing_error(self):
        corpus_dir = os.path.join("tests", "testdata", "dir_invalid")
        header_file = os.path.join("tests", "testdata", "header.xml")
        header_handler = TeiHeaderHandlerImpl(header_file)
        corpus_files = [
            os.path.join(corpus_dir, file) for file in os.listdir(corpus_dir)
        ]
        partition = Partition(header_handler, corpus_files, self.xmlid_handler)
        with self.assertLogs() as logged:
            partition.write_partition(self.mock_stream.path())
        self.assertIn("tests/testdata/dir_invalid/invalid.xml", logged.output[0])

    def test_redundant_elements_with_xml_id_attribute_removed(self):
        corpus_dir = os.path.join("tests", "testdata", "cleaning")
        header_file = os.path.join(corpus_dir, "header.xml")
        corpus_files = [
            os.path.join(corpus_dir, file) for file in os.listdir(corpus_dir)
        ]
        header_handler = TeiHeaderHandlerImpl(header_file)
        partition = Partition(
            header_handler, corpus_files, self.xmlid_handler, clean_files=True
        )
        partition.write_partition(self.mock_stream.path())
        self.mock_stream.output_file.seek(0)
        doc = etree.parse(self.mock_stream.output_file)
        redundant_elements = ["funder", "respStmt", "editorialDecl", "tagsDecl"]
        for elem_tag in redundant_elements:
            result = doc.findall(
                f".//{elem_tag}", namespaces={None: "http://www.tei-c.org/ns/1.0"}
            )
            with self.subTest():
                self.assertEqual(len(result), 1)

    def test_xmlid_attributes_prefixed(self):
        corpus_dir = os.path.join("tests", "testdata", "cleaning")
        header_file = os.path.join(corpus_dir, "header.xml")
        corpus_files = [
            os.path.join(corpus_dir, file) for file in os.listdir(corpus_dir)
        ]
        header_handler = TeiHeaderHandlerImpl(header_file)
        xmlid_handler = XmlIdPrefixer()
        partition = Partition(
            header_handler, corpus_files, xmlid_handler, clean_files=False
        )
        partition.write_partition(self.mock_stream.path())
        self.mock_stream.output_file.seek(0)
        doc = etree.parse(self.mock_stream.output_file)
        result = [
            attr_val.startswith("p8e0744-")
            for attr_val in doc.xpath(
                "tei:TEI//@xml:id", namespaces={"tei": "http://www.tei-c.org/ns/1.0"}
            )
        ]
        self.assertTrue(all(result))

    def test_add_prefix_to_xmlid_with_multiple_files(self):
        corpus_dir = os.path.join("tests", "testdata", "cleaning")
        header_file = os.path.join(corpus_dir, "header.xml")
        corpus_files = [
            os.path.join(corpus_dir, file) for file in os.listdir(corpus_dir)
        ] * 4
        header_handler = TeiHeaderHandlerImpl(header_file)
        xmlid_handler = XmlIdPrefixer()
        partition = Partition(
            header_handler, corpus_files, xmlid_handler, clean_files=False
        )
        partition.write_partition(self.mock_stream.path())
        self.mock_stream.output_file.seek(0)
        doc = etree.parse(self.mock_stream.output_file)
        result = {
            attr_val.split("-")[0]
            for attr_val in doc.xpath(
                "tei:TEI//@xml:id", namespaces={"tei": "http://www.tei-c.org/ns/1.0"}
            )
        }
        self.assertEqual(result, {"p8e0744", "p8e07440", "p8e07441", "p8e07442"})

    def test_xml_model_written_to_corpus_file(self):
        xml_pi = [etree.PI("pi1")]
        partition = Partition(
            self.mock_header_handler,
            [],
            self.xmlid_handler,
            processing_instructions=xml_pi,
        )
        partition.write_partition(self.mock_stream.path())
        self.mock_stream.output_file.seek(0)
        file_content = self.mock_stream.output_file.read().decode("utf-8")
        proc_instr = "<?pi1 ?>"
        self.assertTrue(proc_instr in file_content)

    def test_multiple_xml_models_written_to_corpus_file(self):
        xml_pis = [
            etree.PI("pi1"),
            etree.PI("xml-model"),
            etree.PI("pi2", "atr1='val1' atr2='val2'"),
        ]
        partition = Partition(
            self.mock_header_handler,
            [],
            self.xmlid_handler,
            processing_instructions=xml_pis,
        )
        partition.write_partition(self.mock_stream.path())
        self.mock_stream.output_file.seek(0)
        doc = etree.parse(self.mock_stream.output_file)
        result = [
            (pi.target, pi.attrib) for pi in doc.xpath("preceding-sibling::node()")
        ]
        self.assertEqual(
            result,
            [("pi1", {}), ("xml-model", {}), ("pi2", {"atr1": "val1", "atr2": "val2"})],
        )

    def test_doc_id_added_to_tree(self):
        file = os.path.join("tests", "testdata", "corpus", "file1.xml")
        docid_handler = MockDocIdHandler()
        partition = Partition(
            self.mock_header_handler,
            [file],
            self.xmlid_handler,
            docid_handler=docid_handler,
        )
        partition.write_partition(self.mock_stream.path())
        self.mock_stream.output_file.seek(0)
        doc = etree.parse(self.mock_stream.output_file)
        result = doc.find(".//{*}new")
        self.assertTrue(result is not None)
        self.assertEqual(result.text, file)
