from dataclasses import dataclass
from typing import Dict, Optional, Protocol

from tei_make_corpus.cli.corpus_config import CorpusConfig
from tei_make_corpus.construct_processing_instructions import (
    construct_processing_instructions,
)
from tei_make_corpus.corpus_maker import TeiCorpusMaker
from tei_make_corpus.corpus_stream import CorpusStream
from tei_make_corpus.file_size_estimator import FileSizeEstimatorImpl
from tei_make_corpus.header_handler import TeiHeaderHandlerImpl
from tei_make_corpus.partitioner import Partitioner
from tei_make_corpus.path_finder import PathFinderImpl
from tei_make_corpus.xmlid_handler import create_xmlid_handler


@dataclass
class CliRequest:
    header_file: str
    corpus_dir: str
    output_file: Optional[str] = None
    clean_header: bool = False
    split_docs: int = -1
    split_size: int = -1
    prefix_xmlid: bool = False
    pis: Optional[Dict[str, str]] = None


class TeiMakeCorpusUseCase(Protocol):
    def process(self, request: CliRequest) -> None:
        ...


@dataclass
class TeiMakeCorpusUseCaseImpl:
    """
    Use case that is called by the console script
    """

    out_stream: CorpusStream

    def process(self, request: CliRequest) -> None:
        self.out_stream.set_output_file(request.output_file)
        header_handler = TeiHeaderHandlerImpl(request.header_file)
        path_finder = PathFinderImpl()
        size_estimator = FileSizeEstimatorImpl()
        xmlid_handler = create_xmlid_handler(request.prefix_xmlid)
        processing_instructions = None
        if request.pis is not None:
            processing_instructions = construct_processing_instructions(request.pis)
        partitioner = Partitioner(
            header_handler=header_handler,
            path_finder=path_finder,
            size_estimator=size_estimator,
            xmlid_handler=xmlid_handler,
            xml_processing_instructions=processing_instructions,
        )
        config = CorpusConfig(
            clean_header=request.clean_header,
            split_docs=request.split_docs,
            split_size=request.split_size,
        )
        corpus_maker = TeiCorpusMaker(
            outstream=self.out_stream, partitioner=partitioner, config=config
        )
        corpus_maker.build_corpus(request.corpus_dir, request.header_file)
