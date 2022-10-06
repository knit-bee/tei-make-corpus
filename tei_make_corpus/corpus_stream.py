import sys
from typing import BinaryIO, Protocol, Union


class CorpusStream(Protocol):
    def path(self) -> Union[str, BinaryIO]:
        ...


class CorpusStreamImpl:
    def path(self) -> Union[str, BinaryIO]:
        return sys.stdout.buffer
