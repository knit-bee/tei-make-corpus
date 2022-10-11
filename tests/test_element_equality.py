import random

from lxml import etree

from tei_make_corpus.element_equality import elements_equal


def test_tag_different():
    elem1 = etree.Element("tag")
    elem2 = etree.Element("tag2")
    assert elements_equal(elem1, elem2) is False


def test_tags_equal_but_text_different():
    elem1 = etree.Element("tag")
    elem1.text = "text"
    elem2 = etree.Element("tag")
    elem2.text = "text2"
    assert elements_equal(elem1, elem2) is False
    assert elements_equal(elem2, elem1) is False


def test_tags_equal_but_text_different_whitespace():
    elem1 = etree.Element("tag")
    elem1.text = "    "
    elem2 = etree.Element("tag")
    elem2.text = "text2"
    assert elements_equal(elem1, elem2) is False
    assert elements_equal(elem2, elem1) is False


def test_tags_equal_but_text_different_None():
    elem1 = etree.Element("tag")
    elem2 = etree.Element("tag")
    elem2.text = "text2"
    assert elements_equal(elem1, elem2) is False
    assert elements_equal(elem2, elem1) is False


def test_text_count_as_same():
    elem1 = etree.Element("tag")
    elem2 = etree.Element("tag")
    texts1 = [None, "   ", "   ", "same"]
    texts2 = [None, " ", None, "same"]
    for text1, text2 in zip(texts1, texts2):
        elem1.text = text1
        elem2.text = text2
        assert elements_equal(elem1, elem2) is True
        assert elements_equal(elem2, elem1) is True


def test_elements_attrib_different():
    elem1 = etree.Element("tag", attrib={"a": "value"})
    elem2 = etree.Element("tag", attrib={"a": "value2"})
    assert elements_equal(elem1, elem2) is False


def test_elements_attrib_equal():
    elem1 = etree.Element("tag", attrib={"a": "value"})
    elem2 = etree.Element("tag", attrib={"a": "value"})
    assert elements_equal(elem1, elem2) is True


def test_tags_equal_but_tail_different():
    elem1 = etree.Element("tag")
    elem1.tail = "tail1"
    elem2 = etree.Element("tag")
    elem2.tail = "tail2"
    assert elements_equal(elem1, elem2) is False
    assert elements_equal(elem2, elem1) is False


def test_tags_equal_but_tail_different_None():
    elem1 = etree.Element("tag")
    elem1.tail = "tail1"
    elem2 = etree.Element("tag")
    assert elements_equal(elem1, elem2) is False
    assert elements_equal(elem2, elem1) is False


def test_tags_equal_but_tail_different_whitespace():
    elem1 = etree.Element("tag")
    elem1.tail = "tail1"
    elem2 = etree.Element("tag")
    elem2.tail = "    \n"
    assert elements_equal(elem1, elem2) is False
    assert elements_equal(elem2, elem1) is False


def test_tail_count_as_same():
    elem1 = etree.Element("tag")
    elem2 = etree.Element("tag")
    tails1 = [None, "   ", None, "tail", "tail\n   "]
    tails2 = [None, "  ", "   \n", "tail", "tail"]
    for tail1, tail2 in zip(tails1, tails2):
        elem1.tail = tail1
        elem2.tail = tail2
        assert elements_equal(elem1, elem2) is True
        assert elements_equal(elem2, elem1) is True


def test_different_no_of_children():
    elem1 = etree.Element("tag")
    elem2 = etree.Element("tag")
    for _ in range(random.randint(1, 100)):
        etree.SubElement(elem1, "child1")
    for _ in range(random.randint(1, 100)):
        etree.SubElement(elem2, "child2")
    assert elements_equal(elem1, elem2) is False


def test_elements_with_text_tail_and_attributes_recognized_as_equal():
    elem1 = etree.Element("tag", attrib={"key1": "val1", "key2": "val2"})
    elem1.text, elem1.tail = "text", "tail"
    elem2 = etree.Element("tag", attrib={"key1": "val1", "key2": "val2"})
    elem2.text, elem2.tail = "text", "tail"
    assert elements_equal(elem1, elem2) is True


def test_elements_with_same_child_equal():
    elem1 = etree.Element("tag")
    elem2 = etree.Element("tag")
    etree.SubElement(elem1, "child")
    etree.SubElement(elem2, "child")
    assert elements_equal(elem1, elem2)


def test_element_with_multitple_children_equal():
    elem1 = etree.Element("tag")
    elem2 = etree.Element("tag")
    for _ in range(random.randint(1, 100)):
        etree.SubElement(elem1, "child1")
        etree.SubElement(elem2, "child1")
    assert elements_equal(elem1, elem2) is True


def test_elements_with_complex_children_different():
    tags = ["fileDesc", "title", "author", "publicationStmt", "publisher"]
    elem1 = etree.Element("tag")
    elem2 = etree.Element("tag")
    for _ in range(random.randint(1, 100)):
        tag = random.choice(tags)
        child1 = etree.SubElement(elem1, tag)
        child2 = etree.SubElement(elem2, tag)
        if random.random() > 0.5:
            sub_tag = random.choice(tags)
            etree.SubElement(child1, sub_tag)
            etree.SubElement(child2, sub_tag)
    # add a child only to one element
    etree.SubElement(elem1, "different")
    assert elements_equal(elem1, elem2) is False


def test_elements_with_complex_children_equal():
    tags = ["fileDesc", "title", "author", "publicationStmt", "publisher"]
    elem1 = etree.Element("tag")
    elem2 = etree.Element("tag")
    for _ in range(random.randint(1, 100)):
        tag = random.choice(tags)
        child1 = etree.SubElement(elem1, tag)
        child2 = etree.SubElement(elem2, tag)
        if random.random() > 0.5:
            sub_tag = random.choice(tags)
            etree.SubElement(child1, sub_tag)
            etree.SubElement(child2, sub_tag)
    assert elements_equal(elem1, elem2) is True


def test_elements_with_same_children_but_different_order():
    tags = ["fileDesc", "title", "author", "publicationStmt", "publisher"]
    elem1 = etree.Element("tag")
    elem2 = etree.Element("tag")
    for tag in tags:
        etree.SubElement(elem1, tag)
    for tag in reversed(tags):
        etree.SubElement(elem2, tag)
    assert elements_equal(elem1, elem2) is False


def test_elements_equal_if_ns_ignored():
    elem1 = etree.Element("{namespace}tag")
    elem2 = etree.Element("tag")
    assert elements_equal(elem1, elem2, ignore_ns=True) is True


def test_elements_with_children_equal_if_namespace_ignored():
    elem1 = etree.Element("{namespace}tag")
    elem2 = etree.Element("tag")
    for _ in range(random.randint(1, 100)):
        etree.SubElement(elem1, "{namespace}child")
        etree.SubElement(elem2, "child")
    assert elements_equal(elem1, elem2, ignore_ns=True) is True


def test_elements_different_with_namespace_ignored():
    elem1 = etree.Element("{namespace}tag")
    elem2 = etree.Element("tag2")
    assert elements_equal(elem1, elem2, ignore_ns=True) is False
