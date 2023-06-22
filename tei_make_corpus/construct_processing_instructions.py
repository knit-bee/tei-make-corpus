import logging
from typing import Dict, List, Optional

from lxml import etree

logger = logging.getLogger(__name__)


def construct_processing_instructions(
    pi_dict: Dict[str, str]
) -> Optional[List[etree._ProcessingInstruction]]:
    """
    Constructs xml processing instructions from a dictionary that maps
    targets to text.

    In order to parse (pseudo) attributes of the processing instruction
    correctly, the passed text should contain substrings of attribute-
    value pairs, e.g. attr='val', joined by '='. The value should be
    enclosed by quotes.
    Multuiple attribute-value pairs are separated by whitespace.

    Example:
    >>> pi_dict = {"targ1":"href='path/to/sth' attr='val'", "targ2":"val"}
    >>> construct_processing_instructions(pi_dict)
    [<?targ1 href='path/to/sth' attr='val'?>, <?targ2 val?>]
    """
    constructed_pis = _check_pi_targets(pi_dict)
    if constructed_pis:
        return constructed_pis
    return None


def _check_pi_targets(pi_dict: Dict[str, str]) -> List[etree._ProcessingInstruction]:
    valid_pis = []
    for target, text in pi_dict.items():
        try:
            pi = etree.PI(target, text)
        except ValueError:
            logger.warning("Invalid target for xml processing instruction: %s" % target)
            continue
        valid_pis.append(pi)
    return valid_pis
