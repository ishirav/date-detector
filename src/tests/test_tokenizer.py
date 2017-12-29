from unittest import TestCase

from date_detector.detector import Tokenizer

class TokenizerTest(TestCase):

    def _verify(self, text, expected):
        tokenized = '|'.join([text[token.start : token.end] for token in Tokenizer().tokenize(text)])
        self.assertEqual(expected, tokenized)

    def _get_token_types(self, text):
        return ''.join([token.type for token in Tokenizer().tokenize(text)])

    def test_simple(self):
        text = "the temperature is 23 degrees, but it's a bit chilly."
        expected = "the| |temperature| |is| |23| |degrees|, |but| |it|'|s| |a| |bit| |chilly|."
        self._verify(text, expected)

    def test_punctuation_with_whitespace(self):
        text = "ready - - set... go! "
        expected = "ready| - - |set|... |go|! "
        self._verify(text, expected)
        self.assertEqual(self._get_token_types('   '), 'W')
        self.assertEqual(self._get_token_types(' . '), 'O')
        self.assertEqual(self._get_token_types(' 1. '), 'WDO')

    def test_empty(self):
        self._verify('', '')
