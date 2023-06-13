from dataclasses import dataclass
from typing import List, Optional

from lxml import etree


@dataclass
class CorpusConfig:
    clean_header: bool
    split_docs: int = -1
    split_size: int = -1
    processing_instr: Optional[List[etree.PI]] = None
