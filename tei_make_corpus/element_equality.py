from lxml import etree


def elements_equal(
    elem1: etree._Element, elem2: etree._Element, ignore_ns=False
) -> bool:
    """
    # inspired by https://stackoverflow.com/a/24349916
    Check if two xml elements are equal, i.e. their tags, texts, tails
    and attributes are the same. Moreover they must have the same number
    of children and their children must recursively match for tag, text,
    tail, and attributes to be considered as equal.
    """
    if ignore_ns:
        if etree.QName(elem1.tag).localname != etree.QName(elem2.tag).localname:
            return False
    else:
        if elem1.tag != elem2.tag:
            return False
    if elem1.text is None or not elem1.text.strip():
        if elem2.text is not None and elem2.text.strip():
            return False
    else:
        if elem2.text is None:
            return False
        if elem1.text.strip() != elem2.text.strip():
            return False
    if elem1.tail is None or not elem1.tail.strip():
        if elem2.tail is not None and elem2.tail.strip():
            return False
    else:
        if elem2.tail is None:
            return False
        if elem1.tail.strip() != elem2.tail.strip():
            return False
    if elem1.attrib != elem2.attrib:
        return False
    if len(elem1) != len(elem2):
        return False
    return all(
        elements_equal(child1, child2, ignore_ns=ignore_ns)
        for child1, child2 in zip(elem1, elem2)
    )
