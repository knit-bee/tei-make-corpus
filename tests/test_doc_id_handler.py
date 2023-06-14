import unittest

from lxml import etree

from tei_make_corpus.doc_id_handler import DocIdToIdnoHandler


class DocIdToIdnoHandlerTest(unittest.TestCase):
    def setUp(self):
        self.default_handler = DocIdToIdnoHandler()

    def test_idno_added_to_publicationStmt(self):
        doc = etree.XML(
            """
            <TEI xmlns='http://www.tei-c.org/ns/1.0'>
            <teiHeader>
                <fileDesc>
                    <titleStmt/>
                    <publicationStmt>
                        <publisher/>
                    </publicationStmt>
                </fileDesc>
            </teiHeader>
            </TEI>
            """
        )
        self.default_handler.add_doc_id(doc, "path/to/file")
        self.assertTrue(doc.find(".//{*}publicationStmt/{*}idno") is not None)

    def test_idno_element_added_before_availability(self):
        doc = etree.XML(
            """
            <TEI xmlns='http://www.tei-c.org/ns/1.0'>
            <teiHeader>
                <fileDesc>
                    <titleStmt/>
                    <publicationStmt>
                        <publisher/>
                        <availability/>
                    </publicationStmt>
                </fileDesc>
            </teiHeader>
            </TEI>
            """
        )
        self.default_handler.add_doc_id(doc, "path/to/file")
        idno_elem = doc.find(".//{*}idno")
        self.assertEqual(
            idno_elem.getnext().tag, "{http://www.tei-c.org/ns/1.0}availability"
        )

    def test_idno_added_as_last_child_if_no_availability(self):
        doc = etree.XML(
            """
            <TEI xmlns='http://www.tei-c.org/ns/1.0'>
            <teiHeader>
                <fileDesc>
                    <titleStmt/>
                    <publicationStmt>
                        <publisher/>
                        <date/>
                    </publicationStmt>
                </fileDesc>
            </teiHeader>
            </TEI>
            """
        )
        self.default_handler.add_doc_id(doc, "path/to/file")
        pubstmt_elem = doc.find(".//{*}publicationStmt")
        self.assertEqual(pubstmt_elem[-1].tag, "idno")

    def test_new_idno_added_after_existing_idno_regardless_of_siblings(self):
        docs = [
            etree.XML(
                """
                <TEI xmlns='http://www.tei-c.org/ns/1.0'>
                <teiHeader>
                    <fileDesc>
                        <titleStmt/>
                        <publicationStmt>
                            <publisher/>
                            <idno>old</idno>
                            <availability/>
                        </publicationStmt>
                    </fileDesc>
                </teiHeader>
                </TEI>
                """
            ),
            etree.XML(
                """
                <TEI xmlns='http://www.tei-c.org/ns/1.0'>
                <teiHeader>
                    <fileDesc>
                        <titleStmt/>
                        <publicationStmt>
                            <publisher/>
                            <availability/>
                            <idno>old</idno>
                        </publicationStmt>
                    </fileDesc>
                </teiHeader>
                </TEI>
                """
            ),
            etree.XML(
                """
                <TEI xmlns='http://www.tei-c.org/ns/1.0'>
                <teiHeader>
                    <fileDesc>
                        <titleStmt/>
                        <publicationStmt>
                            <publisher/>
                            <availability/>
                            <idno>old</idno>
                            <date/>
                        </publicationStmt>
                    </fileDesc>
                </teiHeader>
                </TEI>
                """
            ),
            etree.XML(
                """
                <TEI xmlns='http://www.tei-c.org/ns/1.0'>
                <teiHeader>
                    <fileDesc>
                        <titleStmt/>
                        <publicationStmt>
                            <publisher/>
                            <idno>old</idno>
                            <date/>
                            <availability/>
                        </publicationStmt>
                    </fileDesc>
                </teiHeader>
                </TEI>
                """
            ),
        ]
        for doc in docs:
            self.default_handler.add_doc_id(doc, "path/to/file")
            old_idno = doc.find(".//{*}idno")
            with self.subTest():
                self.assertEqual(old_idno.getnext().text, "file")

    def test_filename_added_as_text_of_idno_as_default(self):
        doc = etree.XML(
            """
            <TEI xmlns='http://www.tei-c.org/ns/1.0'>
            <teiHeader>
                <fileDesc>
                    <titleStmt/>
                    <publicationStmt>
                        <publisher/>
                        <availability/>
                    </publicationStmt>
                </fileDesc>
            </teiHeader>
            </TEI>
            """
        )
        self.default_handler.add_doc_id(doc, "path/to/file")
        idno_elem = doc.find(".//{*}idno")
        self.assertEqual(idno_elem.text, "file")

    def test_content_added_to_new_p_element_if_publicationStmt_only_contains_p(self):
        doc = etree.XML(
            """
            <TEI xmlns='http://www.tei-c.org/ns/1.0'>
            <teiHeader>
                <fileDesc>
                    <titleStmt/>
                    <publicationStmt>
                        <p/>
                        <p/>
                    </publicationStmt>
                </fileDesc>
            </teiHeader>
            </TEI>
            """
        )
        self.default_handler.add_doc_id(doc, "path/to/file")
        self.assertTrue(doc.find(".//{*}idno") is None)
        self.assertEqual(doc.find(".//{*}publicationStmt")[-1].text, "file")

    def test_idno_added_to_publicationStmt_in_fileDesc(self):
        doc = etree.XML(
            """
            <TEI xmlns='http://www.tei-c.org/ns/1.0'>
            <teiHeader>
                <fileDesc>
                    <titleStmt/>
                    <publicationStmt>
                        <publisher/>
                        <availability/>
                    </publicationStmt>
                </fileDesc>
                <sourceDesc>
                    <biblFull>
                        <titleStmt/>
                        <publicationStmt>
                            <publisher/>
                        </publicationStmt>
                    </biblFull>
                </sourceDesc>
            </teiHeader>
            </TEI>
            """
        )
        self.default_handler.add_doc_id(doc, "path/to/file")
        self.assertTrue(
            doc.find(".//{*}fileDesc/{*}publicationStmt/{*}idno") is not None
        )

    def test_idno_only_added_to_publicationStmt_in_fileDesc_under_teiHeader(self):
        doc = etree.XML(
            """
            <TEI xmlns='http://www.tei-c.org/ns/1.0'>
            <teiHeader>
                <fileDesc>
                    <titleStmt/>
                    <publicationStmt>
                        <publisher/>
                        <availability/>
                    </publicationStmt>
                </fileDesc>
                <sourceDesc>
                    <biblFull>
                        <fileDesc>
                            <titleStmt/>
                            <publicationStmt>
                                <publisher/>
                            </publicationStmt>
                        </fileDesc>
                    </biblFull>
                </sourceDesc>
            </teiHeader>
            </TEI>
            """
        )
        self.default_handler.add_doc_id(doc, "path/to/file")
        self.assertEqual(len(doc.findall(".//{*}idno")), 1)

    def test_idno_not_added_if_correct_publicationStmt_missing(self):
        doc = etree.XML(
            """
            <TEI xmlns='http://www.tei-c.org/ns/1.0'>
            <teiHeader>
                <fileDesc>
                    <titleStmt/>
                </fileDesc>
                <sourceDesc>
                    <biblFull>
                        <fileDesc>
                            <titleStmt/>
                            <publicationStmt>
                                <publisher/>
                            </publicationStmt>
                        </fileDesc>
                    </biblFull>
                </sourceDesc>
            </teiHeader>
            </TEI>
            """
        )
        self.default_handler.add_doc_id(doc, "path/to/file")
        self.assertEqual(len(doc.findall(".//{*}idno")), 0)

    def test_error_logged_if_correct_publicationStmt_not_present(self):
        doc = etree.XML(
            """
            <TEI xmlns='http://www.tei-c.org/ns/1.0'>
            <teiHeader>
                <fileDesc>
                    <titleStmt/>
                </fileDesc>
                <sourceDesc>
                    <biblFull>
                        <titleStmt/>
                        <publicationStmt>
                            <publisher/>
                        </publicationStmt>
                    </biblFull>
                </sourceDesc>
            </teiHeader>
            </TEI>
            """
        )
        with self.assertLogs() as logged:
            self.default_handler.add_doc_id(doc, "path/to/file")
        self.assertIn("ERROR", logged.output[0])

    def test_filepath_logged_if_correct_publicationStmt_not_present(self):
        doc = etree.XML(
            """
            <TEI xmlns='http://www.tei-c.org/ns/1.0'>
            <teiHeader>
                <fileDesc>
                    <titleStmt/>
                </fileDesc>
                <sourceDesc>
                    <biblFull>
                        <titleStmt/>
                        <publicationStmt>
                            <publisher/>
                        </publicationStmt>
                    </biblFull>
                </sourceDesc>
            </teiHeader>
            </TEI>
            """
        )
        with self.assertLogs() as logged:
            self.default_handler.add_doc_id(doc, "path/to/target_file")
        self.assertIn("path/to/target_file", logged.output[0])

    def test_doc_id_added_under_new_p_element_if_publicationStmt_empty(self):
        doc = etree.XML(
            """
            <TEI xmlns='http://www.tei-c.org/ns/1.0'>
            <teiHeader>
                <fileDesc>
                    <titleStmt/>
                    <publicationStmt/>
                </fileDesc>
            </teiHeader>
            </TEI>
            """
        )
        self.default_handler.add_doc_id(doc, "path/to/file")
        self.assertEqual(doc.find(".//{*}publicationStmt/{*}p").text, "file")

    def test_warning_logged_if_publicationStmt_empty(self):
        doc = etree.XML(
            """
            <TEI xmlns='http://www.tei-c.org/ns/1.0'>
            <teiHeader>
                <fileDesc>
                    <titleStmt/>
                    <publicationStmt/>
                </fileDesc>
            </teiHeader>
            </TEI>
            """
        )
        with self.assertLogs() as logged:
            self.default_handler.add_doc_id(doc, "path/to/file")
        self.assertIn("WARNING", logged.output[0])
        self.assertIn("Incomplete <publicationStmt/>", logged.output[0])
