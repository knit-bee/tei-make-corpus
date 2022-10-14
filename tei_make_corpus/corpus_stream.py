import sys
from typing import BinaryIO, Optional, Protocol, Union


class CorpusStream(Protocol):
    def path(self) -> Union[str, BinaryIO]:
        ...


class CorpusStreamImpl:
    def __init__(self, output_file: Optional[str] = None) -> None:
        self.output_file = output_file

    def path(self) -> Union[str, BinaryIO]:
        if self.output_file is not None:
            return self.output_file
        return sys.stdout.buffer

    def set_output_file(self, file: str) -> None:
        self.output_file = file
