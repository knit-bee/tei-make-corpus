from dataclasses import dataclass
from typing import Generator, List, Optional, Tuple

from lxml import etree

from tei_make_corpus.cli.corpus_config import CorpusConfig
from tei_make_corpus.doc_id_handler import DocIdHandler
from tei_make_corpus.file_size_estimator import FileSizeEstimator
from tei_make_corpus.header_handler import TeiHeaderHandler
from tei_make_corpus.partition import Partition
from tei_make_corpus.path_finder import PathFinder
from tei_make_corpus.xmlid_handler import XmlIdHandler


@dataclass
class Partitioner:
    """
    Splits files in corpus directory into parts and creates configured
    Partition for each part.

    header_handler:     implementation of TeiHeaderHandler interface,
                        provides common corpus header and removes elements
                        in individual headers that are repeated in the
                        common header
    path_finder:        implementation of PathFinder protocol, provides
                        list of file paths for the corpus
    size_estimator:     implementation of FileSizeEstimator protocol,
                        provides file sizes of corpus files
    xmlid_handler:      subclass of XmlIdHandler, handles @xml:id in
                        individual TEI documents
    docid_handler:      implementation of DocIdHandler interface, allows
                        adding a document identifier to individual TEI
                        documents
    """

    header_handler: TeiHeaderHandler
    path_finder: PathFinder
    size_estimator: FileSizeEstimator
    xmlid_handler: XmlIdHandler
    docid_handler: Optional[DocIdHandler] = None

    def get_partitions(
        self, corpus_dir: str, header_file: str, config: Optional[CorpusConfig] = None
    ) -> Generator[Partition, None, None]:
        """
        Split files in corpus_dir into Partitions according to configuration.

        corpus_dir:     path to directory containing corpus files
        header_file:    path to file containing common corpus header
        config:         configurations for processing the corpus

        Returns:        generator of Partition
        """
        clean = False
        docs_per_file = -1
        doc_size = -1
        processing_instructions = None
        if config is not None:
            clean = config.clean_header
            docs_per_file = config.split_docs
            doc_size = config.split_size
            processing_instructions = config.processing_instructions
        return self._determine_partitions(
            corpus_dir,
            header_file,
            clean_files=clean,
            docs_per_file=docs_per_file,
            doc_size=doc_size,
            xml_processing_instructions=processing_instructions,
        )

    def _determine_partitions(
        self,
        corpus_dir: str,
        header_file: str,
        clean_files: bool = False,
        docs_per_file: int = -1,
        doc_size: int = -1,
        xml_processing_instructions: Optional[List[etree.PI]] = None,
    ) -> Generator[Partition, None, None]:
        all_files = self.path_finder.get_paths_for_corpus_files(corpus_dir, header_file)
        total_number_files = len(all_files)
        if doc_size != -1:
            index_pairs = self._determine_chunk_indices_file_size(all_files, doc_size)
        else:
            index_pairs = self._determine_chunk_indices_num_docs(
                total_number_files, docs_per_file
            )
        for start_index, end_index in index_pairs:
            yield Partition(
                self.header_handler,
                all_files[start_index:end_index],
                self.xmlid_handler,
                clean_files=clean_files,
                processing_instructions=xml_processing_instructions,
                docid_handler=self.docid_handler,
            )

    def _determine_chunk_indices_num_docs(
        self, total_num_of_files: int, intended_chunk_size: int
    ) -> List[Tuple[int, int]]:
        if total_num_of_files == 0:
            return []
        if intended_chunk_size == -1 or total_num_of_files < intended_chunk_size:
            return [(0, total_num_of_files)]
        num_chunks = total_num_of_files // intended_chunk_size
        # check if last chunk would be smaller than 30% of intended chunk size
        # if yes, distribute files evenly
        if (
            0
            < total_num_of_files - (num_chunks * intended_chunk_size)
            < intended_chunk_size * 0.3
        ):
            indices = []
            start = 0
            for i in range(1, num_chunks + 1):
                end = int(round(i * (total_num_of_files / num_chunks)))
                indices.append((start, end))
                start = end
            return indices
        return [
            (i, i + intended_chunk_size)
            for i in range(0, total_num_of_files, intended_chunk_size)
        ]

    def _determine_chunk_indices_file_size(
        self, all_files: List[str], intended_doc_size: int
    ) -> List[Tuple[int, int]]:
        file_sizes = self.size_estimator.determine_file_sizes(all_files)
        if not file_sizes:
            return []
        if sum(file_sizes) <= intended_doc_size:
            return [(0, len(all_files))]
        indices = []
        summed_size = 0
        start = 0
        i = 0
        for i, size in enumerate(file_sizes):
            summed_size += size
            if summed_size >= intended_doc_size:
                end = i + 1
                indices.append((start, end))
                start = end
                summed_size = 0
        else:
            if start < i + 1:
                indices.append((start, i + 1))
        return indices
