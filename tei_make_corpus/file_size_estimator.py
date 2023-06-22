import os
from typing import List, Protocol


class FileSizeEstimator(Protocol):
    """Interface used by Partitioner for splitting corpus by size"""

    def determine_file_sizes(self, list_of_file_paths: List[str]) -> List[int]:
        ...


class FileSizeEstimatorImpl:
    def determine_file_sizes(self, list_of_file_paths: List[str]) -> List[int]:
        """
        Returns list of files sizes in bytes for file paths in input.

        list_of_file_paths:     list of corpus files
        """
        return [
            os.stat(file).st_size if os.path.exists(file) else 0
            for file in list_of_file_paths
        ]
