from dataclasses import dataclass
from typing import Optional, Protocol

from tei_make_corpus.cli.corpus_config import CorpusConfig
from tei_make_corpus.corpus_maker import TeiCorpusMaker
from tei_make_corpus.corpus_stream import CorpusStream
from tei_make_corpus.file_size_estimator import FileSizeEstimatorImpl
from tei_make_corpus.header_handler import TeiHeaderHandlerImpl
from tei_make_corpus.partitioner import Partitioner
from tei_make_corpus.path_finder import PathFinderImpl


@dataclass
class CliRequest:
    header_file: str
    corpus_dir: str
    output_file: Optional[str] = None
    clean_header: bool = False
    split_docs: int = -1
    split_size: int = -1


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
        partitioner = Partitioner(
            header_handler=header_handler,
            path_finder=path_finder,
            size_estimator=size_estimator,
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
