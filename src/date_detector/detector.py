from __future__ import unicode_literals

from collections import namedtuple
from datetime import date, datetime


# Formats for parsing dates that contain only digits
FORMATS_WITH_DMY = ['%Y/%m/%d', '%y/%m/%d', '%d/%m/%Y', '%d/%m/%y']
FORMATS_WITH_MDY = ['%Y/%m/%d', '%y/%m/%d', '%m/%d/%Y', '%m/%d/%y']

# Acceptable range of dates
DEFAULT_MIN_DATE = date(1950, 1, 1)
DEFAULT_MAX_DATE = date(2049, 12, 31)

Match = namedtuple('Match', 'date offset text')

Entry = namedtuple('Entry', 'year month day token')

Candidate = namedtuple('Candidate', 'year month day')

Token = namedtuple('Token', 'start end type')


class Tokenizer(object):
    '''
    Breaks text into a sequence of consecutive tokens. Each token
    has a type, which can be digits, letters, whitespace or other.
    The "whitespace" token type is a pure sequence of whitespace
    characters, while "other" can contain a mixture of punctuation,
    whitespace, and any other non-alphanumeric characters.
    '''

    # Token types
    DIGITS      = 'D'
    LETTERS     = 'L'
    WHITESPACE  = 'W'
    OTHER       = 'O'

    # Characters that are considered whitespace
    WHITESPACE_CHARS = ' \t\n\r'.encode('ascii')

    def tokenize(self, text):
        '''
        Returns a generator of Token instances found in the text.
        '''
        token_start = token_end = 0
        token_type = None
        for char in text:
            char_type = self._char_type(char)
            if token_type is None or token_type == char_type:
                # Current token continues
                token_type = char_type
                token_end += 1
            elif (token_type == self.WHITESPACE and char_type == self.OTHER or
                  token_type == self.OTHER and char_type == self.WHITESPACE):
                # Whitespace joins other
                token_type = self.OTHER
                token_end += 1
            else:
                # Current token ends
                yield Token(token_start, token_end, token_type)
                token_type = char_type
                token_start = token_end
                token_end = token_start + 1
        # Yield the last token
        if token_type:
            yield Token(token_start, token_end, token_type)

    def _char_type(self, char):
        '''
        Determines the type of the given character.
        '''
        if char.isdigit():
            return self.DIGITS
        if char.isalpha():
            return self.LETTERS
        if char in self.WHITESPACE_CHARS:
            return self.WHITESPACE
        return self.OTHER


class Sequence(object):
    '''
    Holds a sequence of tokens and their matching dictionary entries.
    '''

    def __init__(self, text):
        self.text = text
        self.tokens = []
        self.entries = []

    def __repr__(self):
        return '/'.join([self.text[t.start : t.end] for t in self.tokens])

    def __iter__(self):
        return iter(self.entries)

    def add(self, token, entry):
        self.tokens.append(token)
        self.entries.append(entry)

    def is_all_digits(self):
        return all((t.type == Tokenizer.DIGITS for t in self.tokens))

    def is_full(self):
        return len(self.tokens) == 3

    def get_start(self):
        return self.tokens[0].start

    def get_end(self):
        return self.tokens[-1].end

    def get_text(self):
        return self.text[self.get_start() : self.get_end()]


class Parser(object):

    def __init__(self, dictionaries=('en',), month_before_day=False,
                 min_date=DEFAULT_MIN_DATE, max_date=DEFAULT_MAX_DATE, tokenizer_class=Tokenizer):
        self.month_before_day = month_before_day
        self.min_date = min_date
        self.max_date = max_date
        self.tokenizer = tokenizer_class()
        self.entries = {}
        self._build_default_dictionary()
        for d in dictionaries:
            self._load_dictionary(d)

    def parse(self, text):
        seq = Sequence(text)
        for token in self.tokenizer.tokenize(text):
            # Look for the token text in the dictionaries
            token_text = self._extract_token(text, token)
            entry = self.entries.get(token_text)
            if entry is None:
                # Token not identified, end of current token sequence (if any)
                for match in self._build_matches(seq):
                    yield match
                seq = Sequence(text)
            else:
                # Should this token be skipped?
                if not (entry.year or entry.month or entry.day):
                    continue
                # Add the token to the current sequence
                seq.add(token, entry)
                # End the sequence if it is full
                if seq.is_full():
                    for match in self._build_matches(seq):
                        yield match
                    seq = Sequence(text)
        # Yield any remaining matches
        for match in self._build_matches(seq):
            yield match

    def _extract_token(self, text, token):
        '''
        Extracts the token from the text and preprocesses it:
        - DIGITS remain the same
        - LETTERS are converted to lowercase
        - WHITESPACE of any kind is converted to blanks
        - OTHER is stripped of whitespace
        '''
        token_text = text[token.start: token.end]
        if token.type == Tokenizer.LETTERS:
            token_text = token_text.lower()
        elif token.type == Tokenizer.WHITESPACE:
            token_text = ' ' * len(token_text)
        elif token.type == Tokenizer.OTHER:
            token_text = token_text.strip()
        return token_text

    def _build_matches(self, seq):
        matches = set()
        if seq.is_full():
            candidates = self._digits_candidates(seq) if seq.is_all_digits() else self._mixed_candidates(seq)
            for candidate in candidates:
                try:
                    d = date(*candidate)
                    matches.add(Match(date=d, offset=seq.get_start(), text=seq.get_text()))
                except ValueError:
                    pass
        return matches

    def _digits_candidates(self, seq):
        text = repr(seq)
        formats = FORMATS_WITH_MDY if self.month_before_day else FORMATS_WITH_DMY
        candidates = []
        for f in formats:
            try:
                d = datetime.strptime(text, f).date()
                if self.min_date <= d <= self.max_date:
                    candidates.append(Candidate(d.year, d.month, d.day))
            except Exception as e:
                pass
        return candidates

    def _mixed_candidates(self, seq):
        candidates = [Candidate(None, None, None)]
        for entry in seq:
            candidates = self._extend(candidates, entry)
        return candidates

    def _extend(self, candidates, entry):
        new_candidates = []
        if entry.year:
            # Create new candidates by filling their year field
            new_candidates.extend([Candidate(entry.year, c.month, c.day) for c in candidates if not c.year])
        if entry.month:
            # Create new candidates by filling their month field
            new_candidates.extend([Candidate(c.year, entry.month, c.day) for c in candidates if not c.month])
        if entry.day:
            # Create new candidates by filling their day field
            new_candidates.extend([Candidate(c.year, c.month, entry.day) for c in candidates if not c.day])
        return new_candidates

    def _add_to_dictionary(self, token, year=None, month=None, day=None):
        token = token.lower()
        old_entry = self.entries.get(token)
        if old_entry:
            entry = Entry(
                year or old_entry.year,
                month or old_entry.month,
                day or old_entry.day,
                token
            )
        else:
            entry = Entry(year, month, day, token)
        self.entries[token] = entry

    def _build_default_dictionary(self):
        # Valueless tokens and whitespace
        for token in ',./\\-':
            self._add_to_dictionary(token)
        for n in range(1, 4):
            self._add_to_dictionary(' ' * n)
        # Years
        for year in range(self.min_date.year, self.max_date.year + 1):
            self._add_to_dictionary(str(year), year=year)
            self._add_to_dictionary(str(year)[2:], year=year)
        # Months
        for month in range(1, 13):
            self._add_to_dictionary(str(month), month=month)
            if month < 10:
                self._add_to_dictionary('0' + str(month), month=month)
        # Days
        for day in range(1, 32):
            self._add_to_dictionary(str(day), day=day)
            if day < 10:
                self._add_to_dictionary('0' + str(day), day=day)

    def _load_dictionary(self, name):
        from pkgutil import get_data
        text = get_data('date_detector', 'dictionaries/%s.txt' % name)
        for line in text.decode('utf-8').splitlines():
            line = line.strip()
            if not line or line[0] == '#':
                continue
            parts = line.split()
            if len(parts) != 4:
                raise ValueError('Invalid line in %s dictionary: "%s"' % line)
            self._add_to_dictionary(
                parts[0],
                None if parts[1] == '-' else int(parts[1]),
                None if parts[2] == '-' else int(parts[2]),
                None if parts[3] == '-' else int(parts[3])
            )
