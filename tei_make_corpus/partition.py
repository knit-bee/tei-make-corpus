import logging
from dataclasses import dataclass
from typing import BinaryIO, List, Optional, Union

from lxml import etree

from tei_make_corpus.header_handler import TeiHeaderHandler
from tei_make_corpus.xmlid_handler import XmlIdHandler

logger = logging.getLogger(__name__)


@dataclass
class Partition:
    header_handler: TeiHeaderHandler
    files: List[str]
    xmlid_handler: XmlIdHandler
    clean_files: bool = False
    processing_instructions: Optional[List[etree.PI]] = None

    def write_partition(self, path: Union[str, BinaryIO]) -> None:
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
        return root

    def __len__(self):
        return len(self.files)
