import unittest

from lxml import etree

from tei_make_corpus.xmlid_handler import XmlIdHandlerImpl


class XmlIdHandlerImplTest(unittest.TestCase):
    def setUp(self):
        self.xmlid_handler = XmlIdHandlerImpl()

    def test_remove_xmlid_attribute_from_element(self):
        doc = etree.fromstring("<root><one xml:id='a'><two xml:id='b'/></one></root>")
        self.xmlid_handler.process_document(doc)
        result = doc.findall(".//*[@{http://www.w3.org/XML/1998/namespace}id]")
        self.assertEqual(result, [])
