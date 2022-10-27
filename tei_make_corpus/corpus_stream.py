import itertools
import sys
from typing import BinaryIO, Optional, Protocol, Union


class CorpusStream(Protocol):
    def path(self) -> Union[str, BinaryIO]:
        ...

    def set_output_file(self, file: Optional[str]) -> None:
        ...

    def update_output_file_name(self) -> None:
        ...


class CorpusStreamImpl:
    def __init__(self, output_file: Optional[str] = None) -> None:
        self.output_file = output_file
        self._file_name_template: Optional[str] = None
        self._counter: itertools.count = itertools.count(1)

    def path(self) -> Union[str, BinaryIO]:
        if self.output_file is not None:
            return self.output_file
        return sys.stdout.buffer

    def set_output_file(self, file: Optional[str]) -> None:
        if file is not None:
            self.output_file = file

    def update_output_file_name(self) -> None:
        if self._file_name_template is None:
            self._file_name_template = self._find_template_name()
        i = next(self._counter)
        self.output_file = f"{self._file_name_template}{i:04}.xml"

    def _find_template_name(self) -> str:
        if self.output_file is None:
            return "part"
        xml_file_extension = ".xml"
        if self.output_file.endswith(xml_file_extension):
            return self.output_file[: -len(xml_file_extension)]
        return self.output_file
