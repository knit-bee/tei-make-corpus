import sys
import unittest

from tei_make_corpus.corpus_stream import CorpusStreamImpl


class CorpusStreamTest(unittest.TestCase):
    def setUp(self):
        self.corpus_stream = CorpusStreamImpl()

    def test_returns_stdout_buffer(self):
        result = self.corpus_stream.path()
        self.assertEqual(result, sys.stdout.buffer)
