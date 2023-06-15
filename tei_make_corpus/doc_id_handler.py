import logging
import os
import re
from typing import Optional, Protocol

from lxml import etree

logger = logging.getLogger(__name__)


class DocIdHandler(Protocol):
    def add_doc_id(self, doc_root: etree._Element, file_path: str) -> None:
        ...


class DocIdToIdnoHandler:
    """
    Add a doc identifier as content of an <idno/> element to
    teiHeader/fileDesc/publicationStmt. As default, it is assumed that
    the file path is passed as input and the basename of this file path is
    added as identifier.
    To extract only part of the input string, a regex pattern with
    exactly one capturing group can be used to initialize DocIdToIdnoHandler.
    """

    def __init__(self, doc_id_pattern: Optional[str] = None) -> None:
        """
        doc_id_pattern: Optional[str]   A string that can be compiled to
                                        a regex pattern with one capturing
                                        group, where the group encompasses
                                        the part to be added as doc id.
        """
        self._doc_id_pattern = self._check_regex_pattern(doc_id_pattern)

    def add_doc_id(self, doc_root: etree._Element, file_path: str) -> None:
        """
        Add a <idno/> element as child of teiHeader/fileDesc/publicationStmt
        containing the basename of file_path, or, if a doc_id_pattern was
        set,the corresponding part of the filepath.
        The new <idno/> element is as following sibling of the last <idno/>,
        if present, or before any <availability/> element, if present;
        otherwise it is added as last child of <publicationStmt/>.

        doc_root: etree._Element        Root element of a element tree
                                        representing a TEI document
        file_path: str                  A string from which the document
                                        id is extracted. As default, the
                                        basename (i.e. the part of the
                                        string after the last slash) is
                                        used. If a doc_id_pattern was set,
                                        it will be used to search file_path.
        """
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
        new_idno.text = self._extract_doc_id(file_path)
        insertion_index = self._determine_insertion_index(publstmt_elem)
        publstmt_elem.insert(insertion_index, new_idno)

    def _determine_insertion_index(self, parent: etree._Element) -> int:
        insertion_index = len(parent)
        if (idno_siblings := parent.findall("{*}idno")) != []:
            insertion_index = parent.index(idno_siblings[-1]) + 1
        elif (availability_siblings := parent.findall("{*}availability")) != []:
            insertion_index = parent.index(availability_siblings[0])
        return insertion_index

    def _check_regex_pattern(self, pattern: Optional[str]) -> Optional[re.Pattern]:
        if pattern:
            compiled = re.compile(pattern)
            if compiled.groups != 1:
                raise ValueError
            return compiled
        return None

    def _extract_doc_id(self, file_path: str) -> str:
        if self._doc_id_pattern is not None:
            doc_id = self._doc_id_pattern.search(file_path)
            if doc_id:
                return doc_id.group(1)
            logger.warning(
                "Couldn't match file %s with regex '%s'"
                % (file_path, self._doc_id_pattern.pattern)
            )
        return os.path.basename(file_path)
