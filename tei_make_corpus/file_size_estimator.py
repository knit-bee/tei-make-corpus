import os
from typing import List, Protocol


class FileSizeEstimator(Protocol):
    def determine_file_sizes(self, list_of_file_paths: List[str]) -> List[int]:
        ...


class FileSizeEstimatorImpl:
    def determine_file_sizes(self, list_of_file_paths: List[str]) -> List[int]:
        return [
            os.stat(file).st_size if os.path.exists(file) else 0
            for file in list_of_file_paths
        ]
