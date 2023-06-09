import unittest

from lxml import etree

from tei_make_corpus.xmlid_handler import XmlIdPrefixer, XmlIdRemover


class XmlIdHandlerImplTest(unittest.TestCase):
    def setUp(self):
        self.default_handler = XmlIdRemover()
        self.prefix_handler = XmlIdPrefixer()

    def test_remove_xmlid_attribute_from_element(self):
        doc = etree.XML("<root><one xml:id='a'><two xml:id='b'/></one></root>")
        self.default_handler.process_document(doc, "file.xml")
        result = doc.findall(".//*[@{http://www.w3.org/XML/1998/namespace}id]")
        self.assertEqual(result, [])

    def test_xmlid_attribute_from_root_removed(self):
        doc = etree.XML("<root xml:id='a'><inner/></root>")
        self.default_handler.process_document(doc, "file.xml")
        self.assertEqual(doc.attrib, {})

    def test_generate_prefix(self):
        filename = "path/to/file.xml"
        result = self.prefix_handler.generate_prefix(filename)
        self.assertEqual(result, "p0cf83b")

    def test_prefix_shifted_if_collision_occurs(self):
        files = ["path/to/file.xml"] * 100
        result = [self.prefix_handler.generate_prefix(file) for file in files]
        self.assertEqual(result, ["p0cf83b"] + [f"p0cf83b{i}" for i in range(99)])

    def test_add_prefix_to_xmlid_value(self):
        doc = etree.XML("<root><one xml:id='a'><two xml:id='b'/></one></root>")
        self.prefix_handler.process_document(doc, "file.xml")
        result = [
            node.attrib
            for node in doc.findall(".//*[@{http://www.w3.org/XML/1998/namespace}id]")
        ]
        self.assertEqual(
            result,
            [
                {"{http://www.w3.org/XML/1998/namespace}id": "p054536-a"},
                {"{http://www.w3.org/XML/1998/namespace}id": "p054536-b"},
            ],
        )

    def test_prefix_added_to_referencing_attribute(self):
        doc = etree.XML(
            """
        <root>
            <el1 xml:id='a'/>
            <el2 corresp='#a'/>
        </root>
        """
        )
        self.prefix_handler.process_document(doc, "file.xml")
        result = [node.attrib for node in doc]
        self.assertEqual(
            result,
            [
                {"{http://www.w3.org/XML/1998/namespace}id": "p054536-a"},
                {"corresp": "#p054536-a"},
            ],
        )

    def test_prefix_not_added_to_other_attributes(self):
        doc = etree.XML(
            """
            <root>
                <el1 xml:id='a'/>
                <el2 corresp='#a' other='a'/>
                <el3 attr='val'/>
            </root>
            """
        )
        self.prefix_handler.process_document(doc, "file.xml")
        result = [node.attrib for node in doc]
        self.assertEqual(
            result,
            [
                {"{http://www.w3.org/XML/1998/namespace}id": "p054536-a"},
                {"corresp": "#p054536-a", "other": "a"},
                {"attr": "val"},
            ],
        )

    def test_prefix_added_to_attributes_if_other_attributes_before(self):
        doc = etree.XML(
            """
            <root>
                <el1 xml:id='a'/>
                <el2 corresp='#a' other='a' prev='#a'/>
                <el3 attr='val' prev='#a'/>
            </root>
            """
        )
        self.prefix_handler.process_document(doc, "file.xml")
        result = [node.attrib for node in doc]
        self.assertEqual(
            result,
            [
                {"{http://www.w3.org/XML/1998/namespace}id": "p054536-a"},
                {"corresp": "#p054536-a", "other": "a", "prev": "#p054536-a"},
                {"attr": "val", "prev": "#p054536-a"},
            ],
        )

    def test_prefix_not_added_to_attribute_if_not_exact_match_of_value(self):
        doc = etree.XML(
            """
            <root>
                <el1 xml:id='a'/>
                <el2 corresp='#aaa'/>
                <el3 attr='val' prev='ab#a'/>
            </root>
            """
        )
        self.prefix_handler.process_document(doc, "file.xml")
        result = [node.attrib for node in doc]
        self.assertEqual(
            result,
            [
                {"{http://www.w3.org/XML/1998/namespace}id": "p054536-a"},
                {"corresp": "#aaa"},
                {"attr": "val", "prev": "ab#a"},
            ],
        )

    def test_prefix_added_to_multiple_referencing_attributes(self):
        doc = etree.XML(
            """
            <root>
                <el1 xml:id='a'/>
                <el2 prev='#a' />
                <el3 sameAs='#a'/>
                <el4 exclude='#a'/>
            </root>
            """
        )
        self.prefix_handler.process_document(doc, "file.xml")
        result = [node.attrib for node in doc]
        self.assertEqual(
            result,
            [
                {"{http://www.w3.org/XML/1998/namespace}id": "p054536-a"},
                {"prev": "#p054536-a"},
                {"sameAs": "#p054536-a"},
                {"exclude": "#p054536-a"},
            ],
        )

    def test_multiple_xmlid_prefixed_and_referenced(self):
        doc = etree.XML(
            """
            <root>
                <el1 xml:id='a'/>
                <el2 xml:id='b' prev='#a'/>
                <el3 xml:id='c' prev='#b'>
                    <el1 sameAs='#a'/>
                </el3>
                <el4 xml:id='d' prev='#c'/>
            </root>
            """
        )
        self.prefix_handler.process_document(doc, "file.xml")
        result = [node.attrib for node in doc.iter()]
        self.assertEqual(
            result,
            [
                {},
                {"{http://www.w3.org/XML/1998/namespace}id": "p054536-a"},
                {
                    "{http://www.w3.org/XML/1998/namespace}id": "p054536-b",
                    "prev": "#p054536-a",
                },
                {
                    "{http://www.w3.org/XML/1998/namespace}id": "p054536-c",
                    "prev": "#p054536-b",
                },
                {"sameAs": "#p054536-a"},
                {
                    "{http://www.w3.org/XML/1998/namespace}id": "p054536-d",
                    "prev": "#p054536-c",
                },
            ],
        )

    def test_change_prefix_on_root(self):
        doc = etree.XML("<root xml:id='b'/>")
        self.prefix_handler.process_document(doc, "file.xml")
        self.assertEqual(
            doc.attrib,
            {"{http://www.w3.org/XML/1998/namespace}id": "p054536-b"},
        )

    def test_attribute_referencing_root_prefixed(self):
        doc = etree.XML("<root xml:id='b'><inner prev='#b'/></root>")
        self.prefix_handler.process_document(doc, "file.xml")
        result = [node.attrib for node in doc.iter()]
        self.assertEqual(
            result,
            [
                {"{http://www.w3.org/XML/1998/namespace}id": "p054536-b"},
                {"prev": "#p054536-b"},
            ],
        )

    def test_add_prefix_to_referencing_attribute_on_root(self):
        doc = etree.XML(
            """
            <root next='#a'>
                <inner xml:id='a'/>
            </root>
            """
        )
        self.prefix_handler.process_document(doc, "file.xml")
        result = [node.attrib for node in doc.iter()]
        self.assertEqual(
            result,
            [
                {"next": "#p054536-a"},
                {"{http://www.w3.org/XML/1998/namespace}id": "p054536-a"},
            ],
        )
