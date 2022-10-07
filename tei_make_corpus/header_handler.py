from lxml import etree


class TeiHeaderHandler:
    def __init__(self, header_file_path: str) -> None:
        self._header_file = header_file_path
        self._cheader = self._construct_common_header(header_file_path)

    def common_header(self):
        return self._cheader

    def declutter_individual_header(self, iheader: etree._Element) -> None:
        pass

    def _construct_common_header(self, header_file: str) -> etree._Element:
        return etree.parse(header_file).getroot()
