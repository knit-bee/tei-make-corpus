import io
import os
import unittest

from lxml import etree

from tei_make_corpus.element_equality import elements_equal
from tei_make_corpus.header_handler import TeiHeaderHandlerImpl


class TeiHeaderHandlerImplTest(unittest.TestCase):
    def setUp(self):
        self.testdata = os.path.join("tests", "testdata")

    def test_common_header_is_etree_element(self):
        header_file = os.path.join(self.testdata, "header.xml")
        header_handler = TeiHeaderHandlerImpl(header_file)
        self.assertTrue(isinstance(header_handler.common_header(), etree._Element))

    def test_common_header_element_constructed_from_xml(self):
        header_file = os.path.join(self.testdata, "header.xml")
        header_handler = TeiHeaderHandlerImpl(header_file)
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
        header_handler = TeiHeaderHandlerImpl(header_file)
        tei_doc = etree.parse(os.path.join(self.testdata, "corpus_header", "file1.xml"))
        iheader = tei_doc.find(".//{*}teiHeader")
        header_handler.declutter_individual_header(iheader)
        self.assertEqual(tei_doc.findall(".//{*}funder"), [])

    def test_simple_element_not_removed_if_different_in_common_header(self):
        header_file = os.path.join(self.testdata, "corpus_header", "header.xml")
        header_handler = TeiHeaderHandlerImpl(header_file)
        tei_doc = etree.parse(os.path.join(self.testdata, "corpus_header", "file1.xml"))
        iheader = tei_doc.find(".//{*}teiHeader")
        header_handler.declutter_individual_header(iheader)
        self.assertTrue(tei_doc.findall(".//{*}titleStmt/{*}author") != [])

    def test_simple_element_not_removed_if_attributes_different(self):
        header_file = os.path.join(self.testdata, "corpus_header", "header.xml")
        header_handler = TeiHeaderHandlerImpl(header_file)
        tei_doc = etree.parse(os.path.join(self.testdata, "corpus_header", "file1.xml"))
        iheader = tei_doc.find(".//{*}teiHeader")
        header_handler.declutter_individual_header(iheader)
        self.assertTrue(tei_doc.findall(".//{*}publicationStmt/{*}availability") != [])

    def test_simple_element_removed_if_attributes_also_match(self):
        header_file = os.path.join(self.testdata, "corpus_header", "header.xml")
        header_handler = TeiHeaderHandlerImpl(header_file)
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
        header_handler = TeiHeaderHandlerImpl(header_file)
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
        header_handler = TeiHeaderHandlerImpl(header_file)
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
        header_handler = TeiHeaderHandlerImpl(header_file)
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
        header_handler = TeiHeaderHandlerImpl(header_file)
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
              <encodingDesc>
              <projectDesc>
                <p>text collected by some means</p>
              </projectDesc>
              <samplingDecl>
                <p>linebreaks in paragraphs have been omitted (except for poems etc.)</p>
                <p>heading lines and footers have been omitted.</p>
                <p>blank lines and multiple blank spaces, including paragraph indents, have not been preserved.</p>
                <p>marginal notes have been omitted.</p>
                <p>font format (size, type) have not been preserved.</p>
                <p>no reproduction of front and back matters.</p>
                <p>preface(s), appendix(ices), index(es) and epilogues (of the author / editor) have been omitted.</p>
                <p>figures and tables have not been preserved.</p>
              </samplingDecl>
            </encodingDesc>
        </teiHeader>"""
        )
        header_handler = TeiHeaderHandlerImpl(header_file)
        tei_doc = etree.XML(
            """<TEI xmlns="http://www.tei-c.org/ns/1.0">
            <teiHeader>
            <fileDesc>
              <titleStmt/>
              <publicationStmt>
                <p/>
              </publicationStmt>
            </fileDesc>
            <encodingDesc>
              <projectDesc>
                <p>text collected by some means</p>
              </projectDesc>
              <samplingDecl>
                <p>linebreaks in paragraphs have been omitted (except for poems etc.)</p>
                <p>heading lines and footers have been omitted.</p>
                <p>blank lines and multiple blank spaces, including paragraph indents, have not been preserved.</p>
                <p>marginal notes have been omitted.</p>
                <p>font format (size, type) have not been preserved.</p>
                <p>no reproduction of front and back matters.</p>
                <p>preface(s), appendix(ices), index(es) and epilogues (of the author / editor) have been omitted.</p>
                <p>figures and tables have not been preserved.</p>
              </samplingDecl>
            </encodingDesc>
          </teiHeader>
          </TEI>"""
        )
        iheader = tei_doc.find(".//{*}teiHeader")
        header_handler.declutter_individual_header(iheader)
        self.assertEqual(tei_doc.findall(".//{*}encodingDesc"), [])

    def test_elements_with_non_ascii_content_removed_if_equal(self):
        header_file = io.BytesIO(
            """<teiHeader>
            <fileDesc>
                <titleStmt>
                    <title>Corpus title</title>
                </titleStmt>
                 <publicationStmt>
                        <publisher>
                        Corpus Publisher
                        </publisher>
                        <address>
                          <addrLine>Äine Straße</addrLine>
                        </address>
                        <pubPlace>Berlin</pubPlace>
                        <date>2022-10-11</date>
                      </publicationStmt>
                <sourceDesc>
                  <p/>
                </sourceDesc>
            </fileDesc>
        </teiHeader>""".encode(
                "utf-8"
            )
        )
        header_handler = TeiHeaderHandlerImpl(header_file)
        tei_doc = etree.XML(
            """<TEI xmlns="http://www.tei-c.org/ns/1.0">
        <teiHeader>
        <fileDesc>
          <titleStmt/>
      <publicationStmt>
        <publisher>Publisher
        </publisher>
        <address>
          <addrLine>Äine Straße</addrLine>
        </address>
        <pubPlace>City</pubPlace>
        <date>2021-10-11</date>
      </publicationStmt>
        </fileDesc>
      </teiHeader>
      </TEI>"""
        )
        iheader = tei_doc.find(".//{*}teiHeader")
        header_handler.declutter_individual_header(iheader)
        self.assertEqual(tei_doc.findall(".//{*}address"), [])

    def test_removal_of_elements_with_same_tag_under_one_parent(self):
        header_file = io.BytesIO(
            b"""<teiHeader>
                    <fileDesc>
                        <titleStmt>
                            <title>Corpus title</title>
                        </titleStmt>
                        <publicationStmt>
                          <publisher>Publisher</publisher>
                          <address>
                            <addrLine>street at city</addrLine>
                            <addrLine>email@example.org</addrLine>
                          </address>
                          <pubPlace>Place</pubPlace>
                          <date>today</date>
                        </publicationStmt>
                    </fileDesc>
                </teiHeader>"""
        )
        header_handler = TeiHeaderHandlerImpl(header_file)
        tei_doc = etree.XML(
            """<TEI xmlns="http://www.tei-c.org/ns/1.0">
                    <teiHeader>
                    <fileDesc>
                      <titleStmt/>
                      <publicationStmt>
                        <publisher>Publisher</publisher>
                          <address>
                            <addrLine>street at city</addrLine>
                            <addrLine>other_email@example.org</addrLine>
                          </address>
                        <pubPlace>some place</pubPlace>
                        <date>yesterday</date>
                      </publicationStmt>
                    </fileDesc>
                  </teiHeader>
                  </TEI>"""
        )
        iheader = tei_doc.find(".//{*}teiHeader")
        header_handler.declutter_individual_header(iheader)
        self.assertEqual(len(tei_doc.findall(".//{*}addrLine")), 1)

    def test_position_indices_at_end_removed_from_xpath(self):
        header_file = io.BytesIO(b"<header/>")
        header_handler = TeiHeaderHandlerImpl(header_file)
        path = "tag/subTag/other[1]"
        self.assertEqual(
            header_handler._clean_position_indices_from_path(path), "tag/subTag/other"
        )

    def test_path_constructed_correctly(self):
        header_file = io.BytesIO(b"<header/>")
        header_handler = TeiHeaderHandlerImpl(header_file)
        path = "tag/subTag/other[1]"
        self.assertEqual(header_handler._adjust_xpath(path), "./tag/subTag/other")

    def test_position_indices_inside_path_removed(self):
        header_file = io.BytesIO(b"<header/>")
        header_handler = TeiHeaderHandlerImpl(header_file)
        path = "tag/subTag/other[1]/someMore/else[19]"
        result = header_handler._clean_position_indices_from_path(path)
        self.assertEqual(result, "tag/subTag/other/someMore/else")

    def test_tag_in_braces_not_removed_during_path_cleaning(self):
        header_file = io.BytesIO(b"<header/>")
        header_handler = TeiHeaderHandlerImpl(header_file)
        path = "tag[tag2]"
        result = header_handler._clean_position_indices_from_path(path)
        self.assertEqual(result, "tag[tag2]")

    def test_attributes_not_removed_from_path_during_cleaning(self):
        header_file = io.BytesIO(b"<header/>")
        header_handler = TeiHeaderHandlerImpl(header_file)
        path = "tag[@class1]"
        result = header_handler._clean_position_indices_from_path(path)
        self.assertEqual(result, "tag[@class1]")

    def test_attribute_with_value_not_removed_from_path_during_cleaning(self):
        header_file = io.BytesIO(b"<header/>")
        header_handler = TeiHeaderHandlerImpl(header_file)
        path = "tag[@class1='value1']"
        result = header_handler._clean_position_indices_from_path(path)
        self.assertEqual(result, "tag[@class1='value1']")

    def assertXmlElementsEqual(self, element1, element2):
        self.assertTrue(elements_equal(element1, element2))
