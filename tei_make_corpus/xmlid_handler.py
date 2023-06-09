import abc
import uuid
from typing import Set

from lxml import etree


class XmlIdHandler(abc.ABC):
    @abc.abstractmethod
    def process_document(self, doc_root: etree._Element, filepath: str) -> None:
        ...


class XmlIdRemover(XmlIdHandler):
    def process_document(self, doc_root: etree._Element, filepath: str) -> None:
        self._remove_all_xmlid_attributes(doc_root)

    def _remove_all_xmlid_attributes(self, tei_doc: etree._Element) -> None:
        tei_doc.attrib.pop("{http://www.w3.org/XML/1998/namespace}id", None)
        for node in tei_doc.findall(".//*[@{http://www.w3.org/XML/1998/namespace}id]"):
            node.attrib.pop("{http://www.w3.org/XML/1998/namespace}id")


class XmlIdPrefixer(XmlIdHandler):
    def __init__(self) -> None:
        self._prefixes: Set[str] = set()

    def process_document(self, doc_root: etree._Element, filepath: str) -> None:
        self._add_prefix_to_xmlid_attributes(doc_root, filepath)

    def generate_prefix(self, filepath: str) -> str:
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
    if prefix_xmlid:
        return XmlIdPrefixer()
    else:
        return XmlIdRemover()
