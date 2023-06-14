import logging
import os
from typing import Protocol

from lxml import etree

logger = logging.getLogger(__name__)


class DocIdHandler(Protocol):
    def add_doc_id(self, doc_root: etree._Element, file_path: str) -> None:
        ...


class DocIdToIdnoHandler:
    def add_doc_id(self, doc_root: etree._Element, file_path: str) -> None:
        publstmt_elem = doc_root.find(".//{*}teiHeader/{*}fileDesc/{*}publicationStmt")
        if publstmt_elem is None:
            logger.error(
                "<publicationStmt> not found: Couldn't add doc id for file: %s"
                % file_path
            )
            return
        if len(publstmt_elem) == 0 or etree.QName(publstmt_elem[0]).localname == "p":
            new_idno = etree.Element("p")
            logger.warning("Incomplete <publicationStmt/> in file: %s" % file_path)
        else:
            new_idno = etree.Element("idno")
        new_idno.text = os.path.basename(file_path)
        insertion_index = self._determine_insertion_index(publstmt_elem)
        publstmt_elem.insert(insertion_index, new_idno)

    def _determine_insertion_index(self, parent: etree._Element) -> int:
        insertion_index = len(parent)

        if (idno_siblings := parent.findall("{*}idno")) != []:
            insertion_index = parent.index(idno_siblings[-1]) + 1
        elif (availability_siblings := parent.findall("{*}availability")) != []:
            insertion_index = parent.index(availability_siblings[-1])
        return insertion_index
