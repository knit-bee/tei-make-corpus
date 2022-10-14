from dataclasses import dataclass
from typing import Protocol, Optional

from tei_make_corpus.corpus_maker import TeiCorpusMaker
from tei_make_corpus.corpus_stream import CorpusStream
from tei_make_corpus.header_handler import TeiHeaderHandlerImpl


@dataclass
class CliRequest:
    header_file: str
    corpus_dir: str
    output_file: Optional[str] = None


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
        corpus_maker = TeiCorpusMaker(
            outstream=self.out_stream, header_handler=header_handler
        )
        corpus_maker.build_corpus(request.corpus_dir, request.header_file)
