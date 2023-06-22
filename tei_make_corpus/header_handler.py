import re
from typing import List, Protocol

from lxml import etree

from tei_make_corpus.element_equality import elements_equal


class TeiHeaderHandler(Protocol):
    """
    Interface providing the common corpus header and functionality to
    deduplicate elements in the individual headers if they are present
    in the common header.
    """

    def common_header(self) -> etree._Element:
        """
        Returns root element of common teiHeader of the corpus.
        """
        ...

    def declutter_individual_header(self, iheader: etree._Element) -> None:
        """
        Removes elements from the header of a TEI document that present
        and identical in the common header.
        """
        ...


class TeiHeaderHandlerImpl:
    tags_no_leftover_sibling = {"distributor", "publisher", "authority"}

    def __init__(self, header_file_path: str) -> None:
        """
        TeiHeaderHandlerImpl is constructed with the file path to the
        common teiHeader of the corpus.
        """
        self._header_file = header_file_path
        self._cheader = self._construct_common_header(header_file_path)

    def common_header(self) -> etree._Element:
        return self._cheader

    def declutter_individual_header(self, iheader: etree._Element) -> None:
        """
        Remove elements from individual teiHeader if they are identical
        to elements in the common header.
        Two elements are considered identical if they have the same tag,
        text, tail, attributes and number of children AND all pairs of
        children are also identical under the same conditions.
        For text and tail comparision, any occurrance of whitespace at the
        beginning and end of the string is stripped to allow for different
        formatting. Also text or tail only containing whitespace are considered
        equal to 'None'.
        For attribute comparision, the order of attributes may differ as long
        as each @key='value' pair is present on both elements.

        """
        for element in self._cheader.iterdescendants():
            if etree.QName(element.tag).localname in self.tags_no_leftover_sibling:
                continue
            matching = self._element_equivalent_in_individual_header(element, iheader)
            for struct_match in matching:
                if elements_equal(element, struct_match, ignore_ns=True):
                    struct_match.getparent().remove(struct_match)
        for element in self._cheader.iterdescendants(self.tags_no_leftover_sibling):
            matching = self._element_equivalent_in_individual_header(element, iheader)
            for struct_match in matching:
                if elements_equal(element, struct_match, ignore_ns=True):
                    if struct_match.getnext() is None:
                        struct_match.getparent().replace(
                            struct_match, etree.Element("p")
                        )

    def _construct_common_header(self, header_file: str) -> etree._Element:
        return etree.parse(header_file).getroot()

    def _element_equivalent_in_individual_header(
        self, element: etree._Element, iheader: etree._Element
    ) -> List[etree._Element]:
        cheader_tree = self._cheader.getroottree()
        elem_xpath = cheader_tree.getelementpath(element)
        return iheader.findall(
            self._adjust_xpath(elem_xpath),
            namespaces={None: "http://www.tei-c.org/ns/1.0"},
        )

    def _adjust_xpath(self, xpath: str) -> str:
        return f"./{self._clean_position_indices_from_path(xpath)}"

    def _clean_position_indices_from_path(self, xpath: str) -> str:
        pattern = r"\[\d+\]"
        return re.sub(pattern, "", xpath)
