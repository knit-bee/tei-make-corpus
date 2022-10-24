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
        self.controller.process_arguments(["corpus", "--common-header", "header.xml"])
        self.assertEqual(self.mock_use_case.request.header_file, "header.xml")

    def test_controller_extracts_corpus_directory(self):
        self.controller.process_arguments(["corpus", "--common-header", "header.xml"])
        self.assertEqual(self.mock_use_case.request.corpus_dir, "corpus")

    def test_controller_throws_error_if_header_file_is_missing(self):
        with self.assertRaises(SystemExit):
            self.controller.process_arguments(["corpus"])

    def test_controller_extracts_output_filename(self):
        self.controller.process_arguments(
            ["corpus", "-c=header.xml", "--to-file", "output.xml"]
        )
        self.assertEqual(self.mock_use_case.request.output_file, "output.xml")

    def test_controller_extracts_output_filename_short(self):
        self.controller.process_arguments(
            ["corpus", "-c=header.xml", "-f", "output.xml"]
        )
        self.assertEqual(self.mock_use_case.request.output_file, "output.xml")

    def test_to_file_default_is_none_if_option_not_used(self):
        self.controller.process_arguments(["corpus", "--common-header", "header.xml"])
        self.assertEqual(self.mock_use_case.request.output_file, None)

    def test_split_documents_option_requires_file_name_argument(self):
        with self.assertRaises(SystemExit):
            self.controller.process_arguments(
                ["corpus", "-c", "header.xml", "--split-documents"]
            )

    def test_controller_extracts_split_documents_option(self):
        self.controller.process_arguments(
            [
                "corpus",
                "-c",
                "header.xml",
                "--to-file",
                "output.xml",
                "--split-documents",
                "100",
            ]
        )
        self.assertEqual(self.mock_use_case.request.split_docs, 100)

    def test_use_default_value_for_number_of_documents_if_no_value_indicated(self):
        self.controller.process_arguments(
            ["corpus", "-c", "header.xml", "--split-documents", "--to-file", "out.xml"]
        )
        self.assertEqual(self.mock_use_case.request.split_docs, 100_000)

    def test_controller_exits_if_wrong_type_is_used_with_split_documents_option(self):
        with self.assertRaises(SystemExit):
            self.controller.process_arguments(
                ["corpus", "-c=head.xml", "-f=out.xml", "--split-documents", "ten"]
            )

    def test_split_chars_option_requires_file_name_argument(self):
        with self.assertRaises(SystemExit):
            self.controller.process_arguments(
                ["corpus", "-c", "header.xml", "--split-chars"]
            )

    def test_controller_extracts_split_chars_option(self):
        self.controller.process_arguments(
            [
                "corpus",
                "-c",
                "header.xml",
                "--to-file",
                "output.xml",
                "--split-chars",
                "1000000",
            ]
        )
        self.assertEqual(self.mock_use_case.request.split_chars, 1_000_000)

    def test_use_default_value_for_number_of_chars_if_no_value_indicated(self):
        self.controller.process_arguments(
            ["corpus", "-c", "header.xml", "--split-chars", "--to-file", "out.xml"]
        )
        self.assertEqual(self.mock_use_case.request.split_chars, 15_000_000)

    def test_controller_exits_if_wrong_type_is_used_with_split_chars_option(self):
        with self.assertRaises(SystemExit):
            self.controller.process_arguments(
                ["corpus", "-c=head.xml", "-f=out.xml", "--split-chars", "ten"]
            )

    def test_split_chars_option_usable_with_underscore_separated_number(self):
        self.controller.process_arguments(
            ["corpus", "-c=head.xml", "-f='out.xml'", "--split-chars", "100_000_000"]
        )
        self.assertEqual(self.mock_use_case.request.split_chars, 100_000_000)

    def test_split_options_mutually_exclusive(self):
        erroneous_input = [
            ["--split-chars", "--split-documents"],
            ["--split-chars", "10", "--split-documents"],
            ["--split-chars", "--split-documents", "10"],
        ]
        for input_args in erroneous_input:
            with self.assertRaises(SystemExit):
                self.controller.process_arguments(
                    ["corpus", "-c", "head.xml", "-f", "out.xml"] + input_args
                )

    def test_non_positive_integers_and_floats_are_rejected_as_values_for_split_options(
        self,
    ):
        wrong_values = [0, -1, 0.5, -10, 1.5, 3333.3]
        split_opts = ["--split-chars", "--split-documents"]
        for option in split_opts:
            for val in wrong_values:
                with self.subTest():
                    with self.assertRaises(SystemExit):
                        self.controller.process_arguments(
                            ["corpus", "-c", "head.xml", "-f", "out", option, f"{val}"]
                        )

    def test_controller_extracts_header_cleaning_option(self):
        self.controller.process_arguments(
            ["corpus", "-c", "header.xml", "--deduplicate-header"]
        )
        self.assertEqual(self.mock_use_case.request.clean_header, True)

    def test_controller_extracts_header_cleaning_option_short(self):
        self.controller.process_arguments(["corpus", "-c", "header.xml", "-d"])
        self.assertEqual(self.mock_use_case.request.clean_header, True)

    def test_header_cleaning_default_is_false(self):
        self.controller.process_arguments(["corpus", "-c", "header.xml"])
        self.assertEqual(self.mock_use_case.request.clean_header, False)
