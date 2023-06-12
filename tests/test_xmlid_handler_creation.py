import tei_make_corpus.xmlid_handler as xh


def test_xmlidhandler_in_subclass_of_abstract_class():
    handler = xh.create_xmlid_handler()
    assert isinstance(handler, xh.XmlIdHandler)


def test_create_default_xmlid_handler():
    handler = xh.create_xmlid_handler()
    assert isinstance(handler, xh.XmlIdRemover)


def test_create_prefix_xmlid_handler():
    handler = xh.create_xmlid_handler(prefix_xmlid=True)
    assert isinstance(handler, xh.XmlIdPrefixer)
