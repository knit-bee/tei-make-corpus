import argparse
from typing import List

from tei_make_corpus.cli.make_corpus_usecase import CliRequest, TeiMakeCorpusUseCase


class TeiMakeCorpusController:
    """
    Parse command line arguments for tei_make_corpus
    """

    def __init__(self, use_case: TeiMakeCorpusUseCase) -> None:
        self.use_case = use_case

    def process_arguments(self, arguments: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Create a *teiCorpus* from a collection of TEI documents. The output will be printed to stdout."
        )
        parser.add_argument(
            "corpus_dir", help="Directory containing the TEI files.", type=str
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
            "--split-documents",
            nargs="?",
            const=100000,
            type=int,
            help="""Use this option to split the teiCorpus into mutliple files. This option
            takes a number of files that are written to one output file. This option requires
            the '--to-file' argument, which will be used as template for the names of all output
            files. The resulting files will be numbered consecutively. For example, if '--split-file 10' is used,
            ten files are written to each output file.
            This option can also be used without passing a value, the default is 100 000 (documents per output file).
        """,
        )
        args = parser.parse_args(arguments)
        if args.split_documents and (args.to_file is None):
            parser.error("--split-documents requires --to-file FILENAME")
        self.use_case.process(
            CliRequest(
                header_file=args.common_header,
                corpus_dir=args.corpus_dir,
                output_file=args.to_file,
                split_docs=args.split_documents,
            )
        )
