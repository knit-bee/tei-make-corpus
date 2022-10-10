from dataclasses import dataclass
from typing import Protocol


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
        pass
