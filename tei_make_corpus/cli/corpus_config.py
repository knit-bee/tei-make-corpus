from dataclasses import dataclass


@dataclass
class CorpusConfig:
    clean_header: bool
    split_docs: int = -1
    split_size: int = -1
