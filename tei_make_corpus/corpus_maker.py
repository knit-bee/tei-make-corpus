import logging
from dataclasses import dataclass

from tei_make_corpus.cli.corpus_config import CorpusConfig
from tei_make_corpus.corpus_stream import CorpusStream
from tei_make_corpus.partitioner import Partitioner

logger = logging.getLogger(__name__)


@dataclass
class TeiCorpusMaker:
    """
    Build a teiCorpus from a teiHeader and multiple TEI files
    """

    outstream: CorpusStream
    partitioner: Partitioner
    config: CorpusConfig

    def build_corpus(self, corpus_dir: str, header_file: str) -> None:
        """
        Iterate over TEI files in the directory and combined them with
        the common header into a single teiCorpus-tree.
        The output is printed stdout as default.
        """
        # init config?
        # partition, write
        for partition in self.partitioner.get_partitions(
            corpus_dir, header_file, clean=self.config.clean_header
        ):
            partition.write_partition(self.outstream.path())
            # self.outstream.update_path()
