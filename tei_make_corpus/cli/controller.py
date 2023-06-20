import argparse
import json
import re
import sys
from typing import Dict, List, Optional, Union

if sys.version_info < (3, 11):
    import tomli as toml
else:
    import tomllib as toml

from tei_make_corpus.cli.docid_pattern_map import PatternMap
from tei_make_corpus.cli.make_corpus_usecase import CliRequest, TeiMakeCorpusUseCase


class TeiMakeCorpusController:
    """
    Parse command line arguments for tei_make_corpus
    """

    def __init__(self, use_case: TeiMakeCorpusUseCase) -> None:
        self.use_case = use_case
        self._doc_id_pattern_mapping = PatternMap()

    def process_arguments(self, arguments: List[str]) -> None:
        config_parser = argparse.ArgumentParser(
            add_help=False,
        )
        config_parser.add_argument(
            "--config",
            "-k",
            default=None,
            help="""Path to config file in TOML format for settings for optional arguments
            (i.e. corpus_dir and --common-header should be still passed as commandline arguments).
            Use [tei-make-corpus] as header or no header. Keys/ argument names should match CL
            argument names but with underscore instead of dash.""",
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
            help="Xml file containing the common header for the whole corpus. This argument is required.",
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
        parser.add_argument(
            "--processing-instructions",
            type=json.loads,
            help="""Add xml processing instructions to the teiCorpus file. If passed as commandline
            argument, the processing instructions should be formatted as a json-parsable string representing
            a dictionary, e.g. '{"a":"b"}' (with double quotes). If a toml file is used, use an inline table
            or, in multi-line format and used with global table header, prefix the sub-table with 'tei-make-corpus'. """,
        )
        parser.add_argument(
            "--add-docid",
            default=None,
            const=0,
            type=int,
            nargs="?",
            choices=self._doc_id_pattern_mapping.keys(),
            help=f"""Add an <idno/> element to teiHeader/fileDesc/publicationStmt to each
            TEI document in the teiCorpus containing a document identifier. The doc id
            is derived from the original filename. If used without value, it defaults to 0,
            i.e. the basename of the file is added as doc id.
            Otherwise, a predefined regex is used to search the filename and extract a
            capturing group that should be added as identifier. If the filename can't be
            matched, the basename is used instead and a warning is logged.
            Possible regular expressions are:
            {self._doc_id_pattern_mapping}
            """,
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
        if (
            args.add_docid is not None
            and args.add_docid not in self._doc_id_pattern_mapping
        ):
            parser.error(f"Invalid value for --add-docid: {args.add_docid}")
        self.use_case.process(
            CliRequest(
                header_file=args.common_header,
                corpus_dir=args.corpus_dir,
                output_file=args.to_file,
                clean_header=args.deduplicate_header,
                split_docs=args.split_documents or -1,
                split_size=args.split_size or -1,
                prefix_xmlid=args.prefix_xmlid,
                processing_instructions=args.processing_instructions,
                docid_pattern_index=args.add_docid,
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
        sub_config = config.get("tei-make-corpus", None)
        if sub_config is not None:
            return sub_config
        return config
