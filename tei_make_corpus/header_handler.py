from typing import Optional, Protocol

from lxml import etree

from tei_make_corpus.element_equality import elements_equal


class TeiHeaderHandler(Protocol):
    def common_header(self) -> etree._Element:
        ...

    def declutter_individual_header(self, iheader: etree._Element) -> None:
        ...


class TeiHeaderHandlerImpl:
    tags_no_leftover_sibling = {"distributor", "publisher", "authority"}

    def __init__(self, header_file_path: str) -> None:
        self._header_file = header_file_path
        self._cheader = self._construct_common_header(header_file_path)

    def common_header(self):
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
        for element in self._cheader.findall(".//*"):
            if etree.QName(element.tag).localname in self.tags_no_leftover_sibling:
                continue
            matching = self._element_equivalent_in_individual_header(element, iheader)
            if matching is not None:
                if elements_equal(element, matching, ignore_ns=True):
                    matching.getparent().remove(matching)
        for element in self._cheader.iterdescendants(self.tags_no_leftover_sibling):
            matching = self._element_equivalent_in_individual_header(element, iheader)
            if matching is not None:
                if elements_equal(element, matching, ignore_ns=True):
                    if matching.getnext() is None:
                        matching.getparent().replace(matching, etree.Element("p"))

    def _construct_common_header(self, header_file: str) -> etree._Element:
        return etree.parse(header_file).getroot()

    def _element_equivalent_in_individual_header(
        self, element: etree._Element, iheader: etree._Element
    ) -> Optional[etree._Element]:
        cheader_tree = self._cheader.getroottree()
        elem_xpath = cheader_tree.getelementpath(element)
        matching = iheader.find(
            "./" + elem_xpath, namespaces={None: "http://www.tei-c.org/ns/1.0"}
        )
        return matching
