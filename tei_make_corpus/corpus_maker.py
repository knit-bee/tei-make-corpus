import os
from dataclasses import dataclass
from typing import Generator

from lxml import etree

from tei_make_corpus.corpus_stream import CorpusStream


@dataclass
class TeiCorpusMaker:
    outstream: CorpusStream

    def build_corpus(self, corpus_dir: str, header_file: str) -> None:
        common_header = etree.parse(header_file)
        with etree.xmlfile(self.outstream.path(), encoding="utf-8") as xf:
            xf.write_declaration()
            with xf.element("teiCorpus", nsmap={None: "http://www.tei-c.org/ns/1.0"}):
                xf.write("\n")
                xf.write(common_header.getroot())
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
            return None
        self._remove_xmlid_attribute(root)
        return root

    def _get_paths_for_corpus_files(
        self, corpus_dir: str, header_file: str
    ) -> Generator[str, None, None]:
        return (
            os.path.join(root, file)
            for root, dirs, files in os.walk(corpus_dir)
            for file in files
            if file != header_file and file.endswith(".xml")
        )

    def _remove_xmlid_attribute(self, tei_doc: etree._Element) -> None:
        for node in tei_doc.findall(".//*[@{http://www.w3.org/XML/1998/namespace}id]"):
            node.attrib.pop("{http://www.w3.org/XML/1998/namespace}id")
