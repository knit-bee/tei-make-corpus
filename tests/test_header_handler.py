import os
import unittest

from lxml import etree

from tei_make_corpus.header_handler import TeiHeaderHandler
from tests.utils import elements_equal


class TeiHeaderHandlerTest(unittest.TestCase):
    def setUp(self):
        self.testdata = os.path.join("tests", "testdata")

    def test_common_header_is_etree_element(self):
        header_file = os.path.join(self.testdata, "header.xml")
        header_handler = TeiHeaderHandler(header_file)
        self.assertTrue(isinstance(header_handler.common_header(), etree._Element))

    def test_common_header_element_constructed_from_xml(self):
        header_file = os.path.join(self.testdata, "header.xml")
        header_handler = TeiHeaderHandler(header_file)
        expected = etree.XML(
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
        )
        result = header_handler.common_header()
        self.assertXmlElementsEqual(result, expected)

    def assertXmlElementsEqual(self, elem1, elem2):
        return elements_equal(elem1, elem2)
