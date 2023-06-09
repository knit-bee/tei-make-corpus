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

    def test_split_size_option_requires_file_name_argument(self):
        with self.assertRaises(SystemExit):
            self.controller.process_arguments(
                ["corpus", "-c", "header.xml", "--split-size"]
            )

    def test_controller_extracts_split_size_option(self):
        self.controller.process_arguments(
            [
                "corpus",
                "-c",
                "header.xml",
                "--to-file",
                "output.xml",
                "--split-size",
                "1000000",
            ]
        )
        self.assertEqual(self.mock_use_case.request.split_size, 1_000_000)

    def test_use_default_value_for_size_if_no_value_indicated(self):
        self.controller.process_arguments(
            ["corpus", "-c", "header.xml", "--split-size", "--to-file", "out.xml"]
        )
        self.assertEqual(self.mock_use_case.request.split_size, 150_000_000)

    def test_controller_exits_if_wrong_type_is_used_with_split_size_option(self):
        with self.assertRaises(SystemExit):
            self.controller.process_arguments(
                ["corpus", "-c=head.xml", "-f=out.xml", "--split-size", "ten"]
            )

    def test_split_size_option_usable_with_underscore_separated_number(self):
        self.controller.process_arguments(
            ["corpus", "-c=head.xml", "-f='out.xml'", "--split-size", "100_000_000"]
        )
        self.assertEqual(self.mock_use_case.request.split_size, 100_000_000)

    def test_split_options_mutually_exclusive(self):
        erroneous_input = [
            ["--split-size", "--split-documents"],
            ["--split-size", "10", "--split-documents"],
            ["--split-size", "--split-documents", "10"],
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
        split_opts = ["--split-size", "--split-documents"]
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

    def test_controller_stores_default_value_for_split_docs_option_if_not_used(self):
        self.controller.process_arguments(["corpus", "-c", "header.xml"])
        self.assertEqual(self.mock_use_case.request.split_docs, -1)

    def test_controller_stores_default_value_for_split_size_option_if_not_used(self):
        self.controller.process_arguments(["corpus", "-c", "header.xml"])
        self.assertEqual(self.mock_use_case.request.split_size, -1)

    def test_valid_type_dimension_conversion(self):
        input_args = [
            "1k",
            "1K",
            "2m",
            "2.1M",
            "3G",
            "3.5g",
            "2.2t",
            "0.4T",
            "1_000",
            "1_000_000",
            "300_000",
            "2_0_0",
        ]
        expected = [
            1000,
            1000,
            2_000_000,
            2_100_000,
            3_000_000_000,
            3_500_000_000,
            2_200_000_000_000,
            400_000_000_000,
            1000,
            1_000_000,
            300000,
            200,
        ]
        for i, split_val in enumerate(input_args):
            with self.subTest():
                self.assertEqual(
                    self.controller.valid_dimension(split_val), expected[i]
                )

    def test_invalid_type_dimension_conversion(self):
        input_args = [
            "ten",
            "1mio",
            "2giga",
            "thousand",
            "4mill",
            "1Mrd",
            "1B",
            "_100",
            "200_",
            "1__00",
        ]
        for i, split_val in enumerate(input_args):
            with self.subTest():
                with self.assertRaises(TypeError):
                    self.controller.valid_dimension(split_val)

    def test_split_values_with_letters_processed_correctly(self):
        split_vals = ["1k", "1.5K", "3m", "2.3M", "3G", "1.3g", "2t", "0.5T"]
        expected = [
            1000,
            1500,
            3000000,
            2300000,
            3000000000,
            1.3 * 10**9,
            2 * 10**12,
            0.5 * 10**12,
        ]
        for i, val in enumerate(split_vals):
            with self.subTest():
                self.controller.process_arguments(
                    [
                        "corpus",
                        "-c",
                        "header.xml",
                        "-f",
                        "output.xml",
                        "--split-documents",
                        val,
                    ]
                )
                self.assertEqual(self.mock_use_case.request.split_docs, expected[i])
                self.mock_use_case.request = None

    def test_xmlid_prefixing_default_is_false(self):
        self.controller.process_arguments(["corpus", "-c", "header.xml"])
        self.assertEqual(self.mock_use_case.request.prefix_xmlid, False)

    def test_controller_extracts_prefix_xmlid_option(self):
        self.controller.process_arguments(
            ["corpus", "-c", "header.xml", "--prefix-xmlid"]
        )
        self.assertEqual(self.mock_use_case.request.prefix_xmlid, True)
