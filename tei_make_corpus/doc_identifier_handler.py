from typing import Protocol

from lxml import etree


class DocIdentifierHandler(Protocol):
    def add_identifier(self, doc_root: etree._Element) -> None:
        ...


class Doc
