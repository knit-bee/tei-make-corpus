import os
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
        self.configs = os.path.join("tests", "testdata", "config")

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

    def test_optional_arguments_read_from_config_file(self):
        cfg = os.path.join(self.configs, "test.cfg")
        self.controller.process_arguments(
            ["corpus", "-c", "header.xml", "--config", cfg]
        )
        result = [
            self.mock_use_case.request.corpus_dir,
            self.mock_use_case.request.header_file,
            self.mock_use_case.request.output_file,
            self.mock_use_case.request.clean_header,
            self.mock_use_case.request.split_docs,
            self.mock_use_case.request.prefix_xmlid,
        ]
        expected = ["corpus", "header.xml", "output.xml", True, 10, True]
        self.assertEqual(result, expected)

    def test_split_docs_and_split_size_in_config_file_mutually_exclusive(self):
        cfg = os.path.join(self.configs, "invalid.cfg")
        with self.assertRaises(SystemExit):
            self.controller.process_arguments(
                ["corpus", "-c", "header.xml", "--config", cfg]
            )

    def test_arguments_can_be_read_from_file_and_cli(self):
        cfg = os.path.join(self.configs, "config.toml")
        self.controller.process_arguments(
            [
                "corpus",
                "-c",
                "header.xml",
                "--config",
                cfg,
                "--to-file",
                "out_file.xml",
            ]
        )
        result = [
            self.mock_use_case.request.split_docs,
            self.mock_use_case.request.output_file,
        ]
        self.assertEqual(result, [10, "out_file.xml"])

    def test_command_line_args_override_config_file(self):
        cfg = os.path.join(self.configs, "test.cfg")
        self.controller.process_arguments(
            [
                "corpus",
                "-c",
                "header.xml",
                "--config",
                cfg,
                "-f",
                "myfile.xml",
                "--split-documents",
                "30k",
            ]
        )
        result = [
            self.mock_use_case.request.output_file,
            self.mock_use_case.request.split_docs,
        ]
        expected = ["myfile.xml", 30_000]
        self.assertEqual(result, expected)

    def test_empty_config_file_normal_default_values_used(self):
        cfg = os.path.join("tests", "testdata", "dir_empty", "empty.xml")
        self.controller.process_arguments(["corpus", "-c", "header.xml", "-k", cfg])
        result = [
            self.mock_use_case.request.output_file,
            self.mock_use_case.request.clean_header,
            self.mock_use_case.request.split_docs,
            self.mock_use_case.request.split_size,
            self.mock_use_case.request.prefix_xmlid,
        ]
        self.assertEqual(result, [None, False, -1, -1, False])

    def test_controller_raises_error_if_config_file_does_not_exist(self):
        with self.assertRaises(SystemExit):
            self.controller.process_arguments(
                ["corpus", "-c", "head.xml", "--config", "some_file"]
            )

    def test_invalid_toml_file(self):
        cfg = os.path.join(self.configs, "invalid2.cfg")
        with self.assertRaises(SystemExit):
            self.controller.process_arguments(
                ["corpus", "-c", "head.xml", "--config", cfg]
            )

    def test_parse_cfg_file_with_table_header(self):
        cfg = os.path.join(self.configs, "table.cfg")
        self.controller.process_arguments(["corpus", "-c", "head.xml", "--config", cfg])
        result = [
            self.mock_use_case.request.split_docs,
            self.mock_use_case.request.clean_header,
            self.mock_use_case.request.prefix_xmlid,
            self.mock_use_case.request.output_file,
        ]
        self.assertEqual(result, [30, False, True, "out.xml"])

    def test_only_relevant_information_parsed_from_cfg_file(self):
        cfg = os.path.join(self.configs, "irrelevant-info.toml")
        self.controller.process_arguments(["corpus", "-c", "head.xml", "--config", cfg])
        result = [
            self.mock_use_case.request.split_size,
            self.mock_use_case.request.clean_header,
            self.mock_use_case.request.prefix_xmlid,
            self.mock_use_case.request.output_file,
        ]
        self.assertEqual(result, [100, True, False, "out.xml"])

    def test_toml_file_with_table_but_without_required_header_uses_default_values(self):
        cfg = os.path.join(self.configs, "missing.toml")
        self.controller.process_arguments(["corpus", "-c", "head.xml", "-k", cfg])
        result = [
            self.mock_use_case.request.split_size,
            self.mock_use_case.request.clean_header,
            self.mock_use_case.request.prefix_xmlid,
            self.mock_use_case.request.output_file,
        ]
        self.assertEqual(
            result,
            [-1, False, False, None],
        )

    def test_toml_file_with_table_without_default_header_and_other_keys_in_main_section(
        self,
    ):
        cfg = os.path.join(self.configs, "mixed.toml")
        self.controller.process_arguments(["corpus", "-c", "head.xml", "-k", cfg])
        result = [
            self.mock_use_case.request.split_size,
            self.mock_use_case.request.clean_header,
            self.mock_use_case.request.prefix_xmlid,
            self.mock_use_case.request.output_file,
        ]
        self.assertEqual(
            result,
            [-1, False, True, "out.xml"],
        )

    def test_controller_extracts_doc_id_option_without_value(self):
        self.controller.process_arguments(["corpus", "-c", "header.xml", "--add-docid"])
        self.assertEqual(self.mock_use_case.request.docid_pattern_index, 0)

    def test_controller_extracts_doc_id_option_with_value(self):
        args = [
            "corpus -c header.xml --add-docid 1",
            "corpus -c header.xml --add-docid=1",
        ]
        for arguments in args:
            with self.subTest():
                self.mock_use_case.request = None
                self.controller.process_arguments(arguments.split())
                self.assertEqual(self.mock_use_case.request.docid_pattern_index, 1)

    def test_default_for_doc_id_option(self):
        self.controller.process_arguments(["corpus", "-c", "header.xml"])
        self.assertIsNone(self.mock_use_case.request.docid_pattern_index)

    def test_invalid_value_for_doc_id_option_raises_error(self):
        with self.assertRaises(SystemExit):
            self.controller.process_arguments(
                ["corpus", "-c", "header.xml", "--add-docid", "10"]
            )

    def test_invalid_type_for_doc_id_option_raises_error(self):
        with self.assertRaises(SystemExit):
            self.controller.process_arguments(
                ["corpus", "-c", "header.xml", "--add-docid", "_(ab)\\.xml"]
            )

    def test_parse_doc_id_option_from_toml_file(self):
        cfg = os.path.join(self.configs, "docid.cfg")
        self.controller.process_arguments(
            ["corpus", "-c", "header.xml", "--config", cfg]
        )
        self.assertEqual(self.mock_use_case.request.docid_pattern_index, 0)

    def test_invalid_index_for_doc_id_option_in_toml_file_raises_error(self):
        cfg = os.path.join(self.configs, "invalid-docid.cfg")
        with self.assertRaises(SystemExit):
            self.controller.process_arguments(
                ["corpus", "-c", "header.xml", "--config", cfg]
            )

    def test_invalid_value_for_doc_id_option_in_toml_file_raises_error(self):
        cfg = os.path.join(self.configs, "invalid-docid2.cfg")
        with self.assertRaises(SystemExit):
            self.controller.process_arguments(
                ["corpus", "-c", "header.xml", "--config", cfg]
            )

    def test_cli_argument_overrides_cfg_file_option_for_doc_id(self):
        cfg = os.path.join(self.configs, "docid.cfg")
        self.controller.process_arguments(
            ["corpus", "-c", "header.xml", "--config", cfg, "--add-docid=1"]
        )
        self.assertEqual(self.mock_use_case.request.docid_pattern_index, 1)

    def test_no_error_raised_if_invalid_value_in_cfg_for_doc_id_but_correct_cli(self):
        cfg = os.path.join(self.configs, "invalid-docid.cfg")
        self.controller.process_arguments(
            ["corpus", "-c", "header.xml", "--config", cfg, "--add-docid=1"]
        )
        self.assertEqual(self.mock_use_case.request.docid_pattern_index, 1)
