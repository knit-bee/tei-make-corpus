import abc
import uuid
from typing import Set

from lxml import etree


class XmlIdHandler(abc.ABC):
    """
    Abstract base class for classes that define treatment of @xml:id
    """

    @abc.abstractmethod
    def process_document(self, doc_root: etree._Element, filepath: str) -> None:
        """
        Process a single TEI document and handle @xml:id's.

        doc_root:   root of element tree of TEI document

        filepath:   path of the original file containing the TEI document
        """
        ...


class XmlIdRemover(XmlIdHandler):
    """
    Remove all @xml:id attributes from document.
    """

    def process_document(self, doc_root: etree._Element, filepath: str) -> None:
        self._remove_all_xmlid_attributes(doc_root)

    def _remove_all_xmlid_attributes(self, tei_doc: etree._Element) -> None:
        tei_doc.attrib.pop("{http://www.w3.org/XML/1998/namespace}id", None)
        for node in tei_doc.findall(".//*[@{http://www.w3.org/XML/1998/namespace}id]"):
            node.attrib.pop("{http://www.w3.org/XML/1998/namespace}id")


class XmlIdPrefixer(XmlIdHandler):
    """
    Prefix @xml:id attributes to disambiguate them in the teiCorpus.
    """

    def __init__(self) -> None:
        self._prefixes: Set[str] = set()

    def process_document(self, doc_root: etree._Element, filepath: str) -> None:
        """
        Disambiguate @xml:id in TEI document by prefixing values of @xml:id
        and attributes referencing them.
        """
        self._add_prefix_to_xmlid_attributes(doc_root, filepath)

    def generate_prefix(self, filepath: str) -> str:
        """
        Generate a prefix for a document by hashing its file path.

        From the file path, a UUID is generated based on SHA-1 and a fixed
        namespace (i.e. a file path will always result in the same prefix).
        The resulting UUID is shortened by clipping it to the first six
        (of 32) hexadecimal digits. To avoid prefix collisions among the
        short prefixes, an inventory is created and reoccuring prefixes
        are extended by a counting index.
        The resulting prefix is concatenated with the letter 'p' (values of
        @xml:id should begin with a letter).

        Example:
        >>> file_path = "corpus/subdir/file_ahfjksd.xml"
        >>> xmlid_handler.generate_prefix(file_path)
        'pa3a300'

        # internal
        # full UUID: a3a300ee5b3752ea82db4d84db32f48d
        # clipped:   a3a300
        # final:     pa3a300
        """
        uid = uuid.uuid5(uuid.NAMESPACE_DNS, filepath).hex
        prefix = uid[:6]
        tmp_prefix = prefix
        suffix_on_collision = 0
        while tmp_prefix in self._prefixes:
            tmp_prefix = f"{prefix}{suffix_on_collision}"
            suffix_on_collision += 1
        self._prefixes.add(tmp_prefix)
        return f"p{tmp_prefix}"

    def _add_prefix_to_xmlid_attributes(
        self, doc_root: etree._Element, filepath: str
    ) -> None:
        prefix = self.generate_prefix(filepath)
        if (
            xmlid_attrib := doc_root.get("{http://www.w3.org/XML/1998/namespace}id")
        ) is not None:
            doc_root.set(
                "{http://www.w3.org/XML/1998/namespace}id",
                f"{prefix}-{xmlid_attrib}",
            )
            self._add_prefix_to_referencing_attributes(doc_root, xmlid_attrib, prefix)

        for node in doc_root.findall(".//*[@{http://www.w3.org/XML/1998/namespace}id]"):
            xmlid_attrib = node.get("{http://www.w3.org/XML/1998/namespace}id")
            node.set(
                "{http://www.w3.org/XML/1998/namespace}id",
                f"{prefix}-{xmlid_attrib}",
            )
            self._add_prefix_to_referencing_attributes(doc_root, xmlid_attrib, prefix)

    def _add_prefix_to_referencing_attributes(
        self, doc_root: etree._Element, xmlid_value: str, prefix: str
    ) -> None:
        for element in doc_root.xpath(f"//*[@*= '#{xmlid_value}']"):
            for attrib, value in element.items():
                if value == "#" + xmlid_value:
                    element.set(attrib, f"#{prefix}-{xmlid_value}")


def create_xmlid_handler(prefix_xmlid: bool = False) -> XmlIdHandler:
    """
    Choose and create instance of XmlIdHandler subclass according to
    'prefix_xmlid' flag.
    As default 'XmlIdRemover' is returned.
    """
    if prefix_xmlid:
        return XmlIdPrefixer()
    else:
        return XmlIdRemover()
