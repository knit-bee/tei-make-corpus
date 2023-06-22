import os
from typing import List, Protocol


class PathFinder(Protocol):
    """
    Interface used by tei_make_corpus.Partitioner to file paths of
    corpus files.
    """

    def get_paths_for_corpus_files(
        self, corpus_dir: str, header_file: str
    ) -> List[str]:
        """
        Returns a list of all file paths in corpus_dir.
        """
        ...


class PathFinderImpl:
    def get_paths_for_corpus_files(
        self, corpus_dir: str, header_file: str
    ) -> List[str]:
        """
        Return a sorted list of all xml file paths in corpus_dir.

        Files that don't end in '.xml' are excluded. If the file containing
        the common header is located on a path under corpus_dir, it is
        ignored as well.
        """
        return sorted(
            (
                os.path.join(root, file)
                for root, dirs, files in os.walk(corpus_dir)
                for file in files
                if file != os.path.basename(header_file) and file.endswith(".xml")
            )
        )
