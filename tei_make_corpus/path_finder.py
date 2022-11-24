import os
from typing import List, Protocol


class PathFinder(Protocol):
    def get_paths_for_corpus_files(
        self, corpus_dir: str, header_file: str
    ) -> List[str]:
        ...


class PathFinderImpl:
    def get_paths_for_corpus_files(
        self, corpus_dir: str, header_file: str
    ) -> List[str]:
        return sorted(
            (
                os.path.join(root, file)
                for root, dirs, files in os.walk(corpus_dir)
                for file in files
                if file != os.path.basename(header_file) and file.endswith(".xml")
            )
        )
