import logging
from dataclasses import dataclass
from typing import BinaryIO, List, Optional, Union

from lxml import etree

from tei_make_corpus.doc_id_handler import DocIdHandler
from tei_make_corpus.header_handler import TeiHeaderHandler
from tei_make_corpus.xmlid_handler import XmlIdHandler

logger = logging.getLogger(__name__)


@dataclass
class Partition:
    """
    Represents a teiCorpus.

    Partition is created with a list of TEI files that form the corpus
    and configuration classes and values.

    header_handler:     implementation of TeiHeaderHandler interface,
                        provides common corpus header and removes elements
                        in individual headers that are repeated in the
                        common header
    files:              list of files paths
    xmlid_handler:      subclass of XmlIdHandler, handles @xml:id in
                        individual TEI documents
    clean_files:        flag determining if individual headers should be
                        cleared of elements already present in the common
                        header. Default is false.
    processing_instructions:
                        list of processing instructions (as lxml.etree.PI),
                        default is None
    docid_handler:      implementation of DocIdHandler interface, allows
                        adding a document identifier to individual TEI
                        documents
    """

    header_handler: TeiHeaderHandler
    files: List[str]
    xmlid_handler: XmlIdHandler
    clean_files: bool = False
    processing_instructions: Optional[List[etree.PI]] = None
    docid_handler: Optional[DocIdHandler] = None

    def write_partition(self, path: Union[str, BinaryIO]) -> None:
        """
        Write teiCorpus according to chosen settings to output stream.
        """
        with etree.xmlfile(path, encoding="UTF-8") as xf:
            xf.write_declaration()
            if self.processing_instructions is not None:
                for pi in self.processing_instructions:
                    xf.write(pi)
            with xf.element("teiCorpus", nsmap={None: "http://www.tei-c.org/ns/1.0"}):
                xf.write("\n")
                xf.write(self.header_handler.common_header())
                xf.write("\n")
                for tei_file in self.files:
                    # clean individual header
                    # remove xmlns from individual TEI node?
                    # handle recurring id attributes
                    xf.write(self._prepare_single_tei_file(tei_file))
                    xf.write("\n")

    def _prepare_single_tei_file(self, file_path: str) -> etree._Element:
        try:
            doc = etree.parse(file_path)
        except etree.XMLSyntaxError:
            logger.exception("File ommitted: %s" % file_path)
            return None
        root = doc.getroot()
        if etree.QName(root.tag).localname != "TEI":
            logger.info("No <TEI> root element found. Ignoring file: %s", file_path)
            return None
        iheader = root.find(".//{*}teiHeader")
        if self.clean_files:
            self.header_handler.declutter_individual_header(iheader)
        self.xmlid_handler.process_document(root, file_path)
        if self.docid_handler is not None:
            self.docid_handler.add_doc_id(root, file_path)
        return root

    def __len__(self):
        return len(self.files)
