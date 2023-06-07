from typing import Protocol

from lxml import etree


class XmlIdHandler(Protocol):
    def process_document(self, doc_root: etree._Element) -> None:
        ...


class XmlIdHandlerImpl:
    def process_document(self, doc_root: etree._Element) -> None:
        self._remove_xmlid_attribute(doc_root)

    def _remove_xmlid_attribute(self, tei_doc: etree._Element) -> None:
        for node in tei_doc.findall(".//*[@{http://www.w3.org/XML/1998/namespace}id]"):
            node.attrib.pop("{http://www.w3.org/XML/1998/namespace}id")
