from dataclasses import dataclass
from typing import Protocol

from tei_make_corpus.corpus_maker import TeiCorpusMaker
from tei_make_corpus.corpus_stream import CorpusStreamImpl
from tei_make_corpus.header_handler import TeiHeaderHandlerImpl


@dataclass
class CliRequest:
    header_file: str
    corpus_dir: str


class TeiMakeCorpusUseCase(Protocol):
    def process(self, request: CliRequest) -> None:
        ...


class TeiMakeCorpusUseCaseImpl:
    """
    Use case that is called by the console script
    """

    def process(self, request: CliRequest) -> None:
        out_stream = CorpusStreamImpl()
        header_handler = TeiHeaderHandlerImpl(request.header_file)
        corpus_maker = TeiCorpusMaker(
            outstream=out_stream, header_handler=header_handler
        )
        corpus_maker.build_corpus(request.corpus_dir, request.header_file)
