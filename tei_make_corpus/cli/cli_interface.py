import logging
import sys

from tei_make_corpus.cli.controller import TeiMakeCorpusController
from tei_make_corpus.cli.make_corpus_usecase import TeiMakeCorpusUseCaseImpl
from tei_make_corpus.corpus_stream import CorpusStreamImpl

logging.basicConfig(
    filename="tei-make-corpus.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s: %(message)s",
)
logger = logging.getLogger()


def main() -> None:
    """
    Main function that represents entry point for console script.
    """
    args = sys.argv[1:]
    out_stream = CorpusStreamImpl()
    use_case = TeiMakeCorpusUseCaseImpl(out_stream)
    controller = TeiMakeCorpusController(use_case)
    controller.process_arguments(args)
