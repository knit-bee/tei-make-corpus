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
            "--cheader",
            "-c",
            help="Xml file containing the common header for the whole corpus.",
            required=True,
        )
        args = parser.parse_args(arguments)
        self.use_case.process(
            CliRequest(header_file=args.cheader, corpus_dir=args.corpus_dir)
        )
