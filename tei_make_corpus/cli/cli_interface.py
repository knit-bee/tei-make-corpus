import sys

from tei_make_corpus.cli.controller import TeiMakeCorpusController
from tei_make_corpus.cli.make_corpus_usecase import TeiMakeCorpusUseCaseImpl


def main() -> None:
    """
    Main function that represents entry point for console script.
    """
    args = sys.argv[1:]
    use_case = TeiMakeCorpusUseCaseImpl()
    controller = TeiMakeCorpusController(use_case)
    controller.process_arguments(args)
