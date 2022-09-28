import os
from typing import Generator, TextIO

from lxml import etree


class TeiCorpusMaker:
    def build_corpus(self, corpus_dir: str, header_file: str, output_file: str) -> None:
        common_header = etree.parse(header_file)
        with open(output_file, "w", encoding="utf-8") as ptr:
            self._write_corpus_start(ptr)
            ptr.write(
                etree.tostring(common_header, encoding="unicode", pretty_print=True)
            )
            for tei_file in self._get_paths_for_corpus_files(corpus_dir, header_file):
                # clean individual header
                # handle recurring id attributes
                ptr.write(
                    etree.tostring(
                        etree.parse(tei_file), encoding="unicode", pretty_print=True
                    )
                )
            self._write_corpus_end_tag(ptr)

    def _write_corpus_start(self, file_ptr: TextIO) -> None:
        print('<?xml version="1.0" encoding="utf-8"?>', file=file_ptr)
        print('<teiCorpus xmlns="http://www.tei-c.org/ns/1.0">', file=file_ptr)

    def _write_corpus_end_tag(self, file_ptr: TextIO) -> None:
        file_ptr.write("</teiCorpus>")

    def _get_paths_for_corpus_files(
        self, corpus_dir: str, header_file: str
    ) -> Generator[str, None, None]:
        return (
            os.path.join(root, file)
            for root, dirs, files in os.walk(corpus_dir)
            for file in files
            if file != header_file and file.endswith(".xml")
        )
