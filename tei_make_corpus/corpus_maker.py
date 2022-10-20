import logging
import os
from dataclasses import dataclass
from typing import Generator

from lxml import etree

from tei_make_corpus.cli.corpus_config import CorpusConfig
from tei_make_corpus.corpus_stream import CorpusStream
from tei_make_corpus.header_handler import TeiHeaderHandler

logger = logging.getLogger(__name__)


@dataclass
class TeiCorpusMaker:
    """
    Build a teiCorpus from a teiHeader and multiple TEI files
    """

    outstream: CorpusStream
    header_handler: TeiHeaderHandler
    config: CorpusConfig

    def build_corpus(self, corpus_dir: str, header_file: str) -> None:
        """
        Iterate over TEI files in the directory and combined them with
        the common header into a single teiCorpus-tree.
        The output is printed stdout as default.
        """
        with etree.xmlfile(self.outstream.path(), encoding="UTF-8") as xf:
            xf.write_declaration()
            with xf.element("teiCorpus", nsmap={None: "http://www.tei-c.org/ns/1.0"}):
                xf.write("\n")
                xf.write(self.header_handler.common_header())
                xf.write("\n")
                for tei_file in self._get_paths_for_corpus_files(
                    corpus_dir, header_file
                ):
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
        if self.config.clean_header:
            self.header_handler.declutter_individual_header(iheader)
        return root

    def _get_paths_for_corpus_files(
        self, corpus_dir: str, header_file: str
    ) -> Generator[str, None, None]:
        return (
            os.path.join(root, file)
            for root, dirs, files in os.walk(corpus_dir)
            for file in files
            if file != os.path.basename(header_file) and file.endswith(".xml")
        )

    def _remove_xmlid_attribute(self, tei_doc: etree._Element) -> None:
        for node in tei_doc.findall(".//*[@{http://www.w3.org/XML/1998/namespace}id]"):
            node.attrib.pop("{http://www.w3.org/XML/1998/namespace}id")
