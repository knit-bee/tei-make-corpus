import itertools
import sys
from typing import BinaryIO, Optional, Protocol, Union


class CorpusStream(Protocol):
    """Interface for a corpus stream"""

    def path(self) -> Union[str, BinaryIO]:
        """Returns file path of output file or file(-like) object"""
        ...

    def set_output_file(self, file: Optional[str]) -> None:
        """Change path of output file"""
        ...

    def update_output_file_name(self) -> None:
        """
        Defines how to update file path of output file if input corpus is
        split into multiple parts.
        """
        ...


class CorpusStreamImpl:
    """
    Provides output stream where teiCorpus is written to.
    As default, stdout is used.
    """

    def __init__(self, output_file: Optional[str] = None) -> None:
        self.output_file = output_file
        self._file_name_template: Optional[str] = None
        self._counter: itertools.count = itertools.count(1)

    def path(self) -> Union[str, BinaryIO]:
        """
        Return path where output is written. Default path is stdout.
        If an output file is set, its path is returned.
        """
        if self.output_file is not None:
            return self.output_file
        return sys.stdout.buffer

    def set_output_file(self, file: Optional[str]) -> None:
        if file is not None:
            self.output_file = file

    def update_output_file_name(self) -> None:
        """
        Update path of output file if output is split into multiple parts
        by adding consecutive numbering to the output file path.
        If no file path was set, 'part0001.xml' is used as template.
        """
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
