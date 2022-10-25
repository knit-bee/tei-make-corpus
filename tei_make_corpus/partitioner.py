import os
from dataclasses import dataclass
from typing import List

from tei_make_corpus.header_handler import TeiHeaderHandler
from tei_make_corpus.partition import Partition


@dataclass
class Partitioner:
    header_handler: TeiHeaderHandler

    def get_partitions(
        self, corpus_dir: str, header_file: str, clean: bool = False
    ) -> List[Partition]:
        # get info about split
        return self._determine_partitions(corpus_dir, header_file, clean_files=clean)

    def _determine_partitions(
        self, corpus_dir: str, header_file: str, clean_files: bool = False
    ) -> List[Partition]:
        # split
        return [
            Partition(
                self.header_handler,
                self._get_paths_for_corpus_files(corpus_dir, header_file),
                clean_files=clean_files,
            )
        ]

    def _get_paths_for_corpus_files(
        self, corpus_dir: str, header_file: str
    ) -> List[str]:
        return sorted(
            (
                os.path.join(root, file)
                for root, dirs, files in os.walk(corpus_dir)
                for file in files
                if file != os.path.basename(header_file) and file.endswith(".xml")
            )
        )
