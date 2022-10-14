import sys
import unittest

from tei_make_corpus.corpus_stream import CorpusStreamImpl


class CorpusStreamTest(unittest.TestCase):
    def setUp(self):
        self.corpus_stream = CorpusStreamImpl()

    def test_returns_stdout_buffer(self):
        result = self.corpus_stream.path()
        self.assertEqual(result, sys.stdout.buffer)

    def test_file_handle_returned_when_set_as_output(self):
        file = "text.xml"
        self.corpus_stream.set_output_file(file)
        self.assertEqual(self.corpus_stream.path(), file)
