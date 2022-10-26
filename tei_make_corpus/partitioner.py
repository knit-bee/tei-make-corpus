from dataclasses import dataclass
from typing import Generator, List, Optional, Tuple

from tei_make_corpus.cli.corpus_config import CorpusConfig
from tei_make_corpus.header_handler import TeiHeaderHandler
from tei_make_corpus.partition import Partition
from tei_make_corpus.path_finder import PathFinder


@dataclass
class Partitioner:
    header_handler: TeiHeaderHandler
    path_finder: PathFinder

    def get_partitions(
        self, corpus_dir: str, header_file: str, config: Optional[CorpusConfig] = None
    ) -> Generator[Partition, None, None]:
        clean = False
        docs_per_file = -1
        if config is not None:
            clean = config.clean_header
            docs_per_file = config.split_docs
        return self._determine_partitions(
            corpus_dir, header_file, clean_files=clean, docs_per_file=docs_per_file
        )

    def _determine_partitions(
        self,
        corpus_dir: str,
        header_file: str,
        clean_files: bool = False,
        docs_per_file: int = -1,
    ) -> Generator[Partition, None, None]:
        all_files = self.path_finder.get_paths_for_corpus_files(corpus_dir, header_file)
        total_number_files = len(all_files)
        for start_index, end_index in self._determine_chunk_indices(
            total_number_files, docs_per_file
        ):
            yield Partition(
                self.header_handler,
                all_files[start_index:end_index],
                clean_files=clean_files,
            )

    def _determine_chunk_indices(
        self, total_num_of_files: int, intended_chunk_size: int
    ) -> List[Tuple[int, int]]:
        if intended_chunk_size == -1 or total_num_of_files < intended_chunk_size:
            return [(0, total_num_of_files)]
        return [
            (i, i + intended_chunk_size)
            for i in range(0, total_num_of_files, intended_chunk_size)
        ]
