import argparse
import re
import sys
from typing import Dict, List, Optional, Union

if sys.version_info < (3, 11):
    import tomli as toml
else:
    import tomllib as toml

from tei_make_corpus.cli.make_corpus_usecase import CliRequest, TeiMakeCorpusUseCase


class TeiMakeCorpusController:
    """
    Parse command line arguments for tei_make_corpus
    """

    def __init__(self, use_case: TeiMakeCorpusUseCase) -> None:
        self.use_case = use_case

    def process_arguments(self, arguments: List[str]) -> None:
        config_parser = argparse.ArgumentParser(
            add_help=False,
        )
        config_parser.add_argument(
            "--config", "-k", default=None, help="Name of the config file"
        )
        conf_args, remaining_argv = config_parser.parse_known_args(arguments)
        defaults = self.parse_config_file(conf_args.config, config_parser)
        parser = argparse.ArgumentParser(
            parents=[config_parser],
            description="""Create a *teiCorpus* from a collection of TEI documents.
                 The output will be printed to stdout as default.""",
        )
        parser.add_argument(
            "corpus_dir",
            help="Directory containing the TEI files. Only file with the extension '.xml' are processed.",
            type=str,
        )
        parser.add_argument(
            "--common-header",
            "-c",
            help="Xml file containing the common header for the whole corpus.",
            required=True,
        )
        parser.add_argument(
            "--to-file",
            "-f",
            default=None,
            metavar="FILENAME",
            help="""Name of output file to write to. If this option is enabled, the
             output is written to the file instead of stdout.""",
        )
        parser.add_argument(
            "--deduplicate-header",
            "-d",
            default=False,
            action="store_true",
            help="""Remove elements from header of individual TEI files that are
            identical in the common header (experimental).
            """,
        )
        split_group = parser.add_mutually_exclusive_group()
        split_group.add_argument(
            "--split-documents",
            nargs="?",
            const=100000,
            type=self.valid_dimension,
            help="""Use this option to split the teiCorpus into multiple files. This option
            takes a NUMBER OF DOCUMENTS that are written to one output file. This option requires
            the '--to-file' argument, which will be used as template for the names of all output
            files. The resulting files will be numbered consecutively. For example, if '--split-documents 10' is used,
            ten files are written to each output file. Each output file will be a valid, stand-alone teiCorpus and the
            same common header is used for all parts. If the last part would contain less than 30%% of the intended number
            of TEI documents, all files will be distributed evenly (i.e. a part may then contain more than the
            indicated number of files).
            This option can also be used without passing a value, the default is 100 000 (documents per output file).
        """,
        )
        split_group.add_argument(
            "--split-size",
            nargs="?",
            const=150_000_000,
            type=self.valid_dimension,
            help="""Use this option to split the teiCorpus into multiple files. This option
            takes an intended FILE SIZE IN BYTES for one output file. This option requires
            the '--to-file' argument, which will be used as template for the file names of all output
            files. The resulting files will be numbered consecutively. For example, if '--split-size 15000' is used,
            when the limit of 15 kilobytes is reached, (after completing the current TEI document) a new output
            file will be used.
            This option can also be used without passing a value, the default is 150 000 000 (bytes per file, 150 MB).""",
        )
        parser.add_argument(
            "--prefix-xmlid",
            default=False,
            action="store_true",
            help="""Add a prefix to @xml:id attributes instead of removing them.
            The prefix is generated from the the document's file path and concatenated
            with the original value of the @xml:id attribute (separated by '-'). For
            each @xml:id attribute, the prefix is also added to attributes referencing
            the @xml:id, i.e. attributes with the same value as @xml:id but with a
            prepended '#'.""",
        )
        parser.set_defaults(**defaults)
        args = parser.parse_args(remaining_argv)
        if args.split_documents and args.split_size:
            parser.error(
                "Only one of the options --split-size or --split-documents can be used."
            )
        if args.split_documents and (args.to_file is None):
            parser.error("--split-documents requires --to-file FILENAME")
        if args.split_size and args.to_file is None:
            parser.error("--split-size requires --to-file FILENAME")
        if not self._validate_split_value(args):
            parser.error("Split value should be greater 0")
        self.use_case.process(
            CliRequest(
                header_file=args.common_header,
                corpus_dir=args.corpus_dir,
                output_file=args.to_file,
                clean_header=args.deduplicate_header,
                split_docs=args.split_documents or -1,
                split_size=args.split_size or -1,
                prefix_xmlid=args.prefix_xmlid,
            )
        )

    def _validate_split_value(
        self,
        args: argparse.Namespace,
    ) -> bool:
        split_val = None
        if args.split_documents is not None:
            split_val = args.split_documents
        if args.split_size is not None:
            split_val = args.split_size
        if split_val is not None and split_val < 1:
            return False
        return True

    def valid_dimension(self, input_string: str) -> int:
        """
        Check if input string only contains valid unit affixes and
        numeric part. If the string is valid, it is converted to
        integer, else a TypeError is thrown.
        """
        mulitiplicators = {
            "k": 10**3,
            "m": 10**6,
            "g": 10**9,
            "t": 10**12,
            "": 1,
        }
        pattern = r"(\d+(_\d+|d*)*\.?\d*)([kKmMgGtT]?)$"
        match = re.match(pattern, input_string)
        if not match:
            raise TypeError
        numeric_part = match.group(1)
        dimension = match.group(3).lower()
        split_val = float(numeric_part) * mulitiplicators[dimension]
        if split_val % 1:
            raise TypeError
        return int(split_val)

    def parse_config_file(
        self, filepath: Optional[str], parser: argparse.ArgumentParser
    ) -> Dict[str, Union[str, int, bool]]:
        config = {}
        if filepath is not None:
            try:
                with open(filepath, "rb") as fp:
                    config = toml.load(fp)
            except FileNotFoundError:
                parser.error("File not found: %s" % filepath)
            except toml.TOMLDecodeError:
                parser.error("Invalid TOML file: %s" % filepath)
        return config
