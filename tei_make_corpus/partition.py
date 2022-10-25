import logging
from dataclasses import dataclass
from typing import BinaryIO, List, Union

from lxml import etree

from tei_make_corpus.header_handler import TeiHeaderHandler

logger = logging.getLogger(__name__)


@dataclass
class Partition:
    header_handler: TeiHeaderHandler
    files: List[str]
    clean_files: bool = False

    def write_partition(self, path: Union[str, BinaryIO]) -> None:
        with etree.xmlfile(path, encoding="UTF-8") as xf:
            xf.write_declaration()
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
        doc = etree.parse(file_path)
        root = doc.getroot()
        if etree.QName(root.tag).localname != "TEI":
            logger.info("No <TEI> root element found. Ignoring file: %s", file_path)
            return None
        self._remove_xmlid_attribute(root)
        iheader = root.find(".//{*}teiHeader")
        if self.clean_files:
            self.header_handler.declutter_individual_header(iheader)
        return root

    def _remove_xmlid_attribute(self, tei_doc: etree._Element) -> None:
        for node in tei_doc.findall(".//*[@{http://www.w3.org/XML/1998/namespace}id]"):
            node.attrib.pop("{http://www.w3.org/XML/1998/namespace}id")
