import io
import os
import unittest

from lxml import etree

from tei_make_corpus.element_equality import elements_equal
from tei_make_corpus.header_handler import TeiHeaderHandler


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

    def test_simple_element_from_individual_header_removed_if_in_common_header(self):
        header_file = os.path.join(self.testdata, "corpus_header", "header.xml")
        header_handler = TeiHeaderHandler(header_file)
        tei_doc = etree.parse(os.path.join(self.testdata, "corpus_header", "file1.xml"))
        iheader = tei_doc.find(".//{*}teiHeader")
        header_handler.declutter_individual_header(iheader)
        self.assertEqual(tei_doc.findall(".//{*}funder"), [])

    def test_simple_element_not_removed_if_different_in_common_header(self):
        header_file = os.path.join(self.testdata, "corpus_header", "header.xml")
        header_handler = TeiHeaderHandler(header_file)
        tei_doc = etree.parse(os.path.join(self.testdata, "corpus_header", "file1.xml"))
        iheader = tei_doc.find(".//{*}teiHeader")
        header_handler.declutter_individual_header(iheader)
        self.assertTrue(tei_doc.findall(".//{*}titleStmt/{*}author") != [])

    def test_simple_element_not_removed_if_attributes_different(self):
        header_file = os.path.join(self.testdata, "corpus_header", "header.xml")
        header_handler = TeiHeaderHandler(header_file)
        tei_doc = etree.parse(os.path.join(self.testdata, "corpus_header", "file1.xml"))
        iheader = tei_doc.find(".//{*}teiHeader")
        header_handler.declutter_individual_header(iheader)
        self.assertTrue(tei_doc.findall(".//{*}publicationStmt/{*}availability") != [])

    def test_simple_element_removed_if_attributes_also_match(self):
        header_file = os.path.join(self.testdata, "corpus_header", "header.xml")
        header_handler = TeiHeaderHandler(header_file)
        tei_doc = etree.XML(
            """
        <TEI xmlns="http://www.tei-c.org/ns/1.0">
            <teiHeader>
                <fileDesc>
                    <publicationStmt>
                        <pubPlace>place</pubPlace>
                        <availability n="test" status="unknown">Some text</availability>
                    </publicationStmt>
                </fileDesc>
            </teiHeader>
        </TEI>
        """
        )
        iheader = tei_doc.find(".//{*}teiHeader")
        header_handler.declutter_individual_header(iheader)
        self.assertEqual(iheader.findall(".//{*}availability"), [])

    def test_element_publisher_not_removed_from_iheader_publicationStmt_if_siblings(
        self,
    ):
        header_file = os.path.join(self.testdata, "corpus_header", "header.xml")
        header_handler = TeiHeaderHandler(header_file)
        tei_doc = etree.XML(
            """<TEI xmlns="http://www.tei-c.org/ns/1.0">
            <teiHeader>
            <fileDesc>
              <titleStmt/>
              <publicationStmt>
                <publisher>Publisher</publisher>
                <pubPlace>some place</pubPlace>
                <availability n="test" status="unknown">Some text</availability>
              </publicationStmt>
            </fileDesc>
          </teiHeader>
          </TEI>"""
        )
        iheader = tei_doc.find(".//{*}teiHeader")
        header_handler.declutter_individual_header(iheader)
        self.assertTrue(iheader.findall(".//{*}publisher") != [])

    def test_element_authority_not_removed_from_iheader_publicationStmt_if_siblings(
        self,
    ):
        header_file = io.BytesIO(
            b"""<teiHeader>
            <fileDesc>
                <titleStmt>
                    <title>Corpus title</title>
                </titleStmt>
                <publicationStmt>
                  <authority>Publisher</authority>
                  <pubPlace>Place</pubPlace>
                  <date>today</date>
                </publicationStmt>
                <sourceDesc>
                  <p/>
                </sourceDesc>
            </fileDesc>
        </teiHeader>"""
        )
        header_handler = TeiHeaderHandler(header_file)
        tei_doc = etree.XML(
            """<TEI xmlns="http://www.tei-c.org/ns/1.0">
            <teiHeader>
            <fileDesc>
              <titleStmt/>
              <publicationStmt>
                <authority>Publisher</authority>
                <pubPlace>some place</pubPlace>
                <availability n="test" status="unknown">Some text</availability>
              </publicationStmt>
            </fileDesc>
          </teiHeader>
          </TEI>"""
        )
        iheader = tei_doc.find(".//{*}teiHeader")
        header_handler.declutter_individual_header(iheader)
        self.assertTrue(iheader.findall(".//{*}authority") != [])

    def test_element_distributor_not_removed_from_iheader_publicationStmt_if_siblings(
        self,
    ):
        header_file = io.BytesIO(
            b"""<teiHeader>
            <fileDesc>
                <titleStmt>
                    <title>Corpus title</title>
                </titleStmt>
                <publicationStmt>
                  <distributor>Publisher</distributor>
                  <pubPlace>Place</pubPlace>
                  <date>today</date>
                </publicationStmt>
                <sourceDesc>
                  <p/>
                </sourceDesc>
            </fileDesc>
        </teiHeader>"""
        )
        header_handler = TeiHeaderHandler(header_file)
        tei_doc = etree.XML(
            """<TEI xmlns="http://www.tei-c.org/ns/1.0">
            <teiHeader>
            <fileDesc>
              <titleStmt/>
              <publicationStmt>
                <distributor>Publisher</distributor>
                <pubPlace>some place</pubPlace>
                <availability n="test" status="unknown">Some text</availability>
              </publicationStmt>
            </fileDesc>
          </teiHeader>
          </TEI>"""
        )
        iheader = tei_doc.find(".//{*}teiHeader")
        header_handler.declutter_individual_header(iheader)
        self.assertTrue(iheader.findall(".//{*}distributor") != [])

    def test_elements_in_publicationStmt_replaced_by_p_if_removed(self):
        header_file = io.BytesIO(
            b"""<teiHeader>
            <fileDesc>
                <titleStmt>
                    <title>Corpus title</title>
                </titleStmt>
                <publicationStmt>
                  <distributor>Publisher</distributor>
                  <pubPlace>Place</pubPlace>
                  <date>today</date>
                </publicationStmt>
                <sourceDesc>
                  <p/>
                </sourceDesc>
            </fileDesc>
        </teiHeader>"""
        )
        header_handler = TeiHeaderHandler(header_file)
        tei_doc = etree.XML(
            """<TEI xmlns="http://www.tei-c.org/ns/1.0">
            <teiHeader>
            <fileDesc>
              <titleStmt/>
              <publicationStmt>
                <distributor>Publisher</distributor>
              </publicationStmt>
            </fileDesc>
          </teiHeader>
          </TEI>"""
        )
        iheader = tei_doc.find(".//{*}teiHeader")
        header_handler.declutter_individual_header(iheader)
        result = [
            child.tag for child in iheader.find(".//{*}publicationStmt").getchildren()
        ]
        self.assertEqual(result, ["p"])

    def test_complex_element_removed_from_individual_header_if_in_common_header(self):
        pass

    def assertXmlElementsEqual(self, element1, element2):
        self.assertTrue(elements_equal(element1, element2))
