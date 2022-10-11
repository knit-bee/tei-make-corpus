import unittest
from typing import Optional

from tei_make_corpus.cli.controller import TeiMakeCorpusController
from tei_make_corpus.cli.make_corpus_usecase import CliRequest


class MockUseCase:
    def __init__(self) -> None:
        self.request: Optional[CliRequest] = None

    def process(self, request: CliRequest) -> None:
        assert not self.request
        self.request = request


class TeiMakeCorpusControllerTest(unittest.TestCase):
    def setUp(self):
        self.mock_use_case = MockUseCase()
        self.controller = TeiMakeCorpusController(self.mock_use_case)

    def test_controller_extracts_header_file_name(self):
        self.controller.process_arguments(["corpus", "--cheader", "header.xml"])
        self.assertEqual(self.mock_use_case.request.header_file, "header.xml")

    def test_controller_extracts_corpus_directory(self):
        self.controller.process_arguments(["corpus", "--cheader", "header.xml"])
        self.assertEqual(self.mock_use_case.request.corpus_dir, "corpus")

    def test_controller_throws_error_if_header_file_is_missing(self):
        with self.assertRaises(SystemExit):
            self.controller.process_arguments(["corpus"])
