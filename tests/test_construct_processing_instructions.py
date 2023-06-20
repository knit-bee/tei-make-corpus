import logging

from lxml import etree

from tei_make_corpus.construct_processing_instructions import (
    construct_processing_instructions,
)


def test_returns_none_if_input_dict_is_empty():
    assert construct_processing_instructions({}) is None


def test_returns_list_of_pi_if_input_not_empty():
    pis = construct_processing_instructions({"a": ""})
    assert isinstance(pis, list)
    assert isinstance(pis[0], etree._ProcessingInstruction)


def test_target_of_processing_instruction_set():
    pis = construct_processing_instructions({"a": ""})
    assert pis[0].target == "a"


def test_attributes_of_processing_instruction_set():
    pis = construct_processing_instructions({"a": "attr='val' at2='val2' at3='val3'"})
    assert pis[0].attrib == {"attr": "val", "at2": "val2", "at3": "val3"}


def test_text_of_processing_instruction_set():
    pis = construct_processing_instructions({"a": "b"})
    assert pis[0].text == "b"


def test_invalid_target_logs_warning(caplog):
    pis_with_invalid = {"a": "b", "1a": "b", "b:a": ""}
    with caplog.at_level(logging.WARNING):
        construct_processing_instructions(pis_with_invalid)
    assert "Invalid target for xml processing instruction: 1a" in caplog.text
    assert "Invalid target for xml processing instruction: b:a" in caplog.text


def test_pi_construction_returns_none_if_all_targets_are_invalid():
    assert construct_processing_instructions({"1a": ""}) is None
