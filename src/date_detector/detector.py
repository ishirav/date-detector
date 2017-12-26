from collections import namedtuple
from datetime import date

Match = namedtuple('Match', 'date offset text')

Entry = namedtuple('Entry', 'token year month day')

Candidate = namedtuple('Candidate', 'year month day')

EMPTY_CANDIDATE = Candidate(None, None, None)

Token = namedtuple('Token', 'start end type')


class Tokenizer(object):

    DIGITS      = 'D'
    LETTERS     = 'L'
    WHITESPACE  = 'W'
    OTHER       = 'O'

    def tokenize(self, text):
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
        if char.isdigit():
            return self.DIGITS
        if char.isalpha():
            return self.LETTERS
        if char in (' \t\n\r'):
            return self.WHITESPACE
        return self.OTHER



class Parser(object):

    def __init__(self, dictionaries=('en',), month_before_day=False,
                 min_year=1950, max_year=2050, tokenizer_class=Tokenizer):
        self.month_before_day = month_before_day
        self.min_year = min_year
        self.max_year = max_year
        self.tokenizer = tokenizer_class()
        self.entries = {}
        self._build_default_dictionary()
        for d in dictionaries:
            self._load_dictionary(d)

    def parse(self, text):
        candidates = None
        seq_start = seq_end = 0
        for token in self.tokenizer.tokenize(text):
            # print
            # Look for the token text in the dictionaries
            token_text = self._extract_token(text, token)
            # print '"%s"' % token_text, token
            entry = self.entries.get(token_text)
            if entry is None:
                # Token not identified, end of current token sequence (if any)
                if candidates:
                    for match in self._build_matches(text, seq_start, seq_end, candidates):
                        yield match
                    candidates = None
            else:
                # Is it a new sequence?
                if not candidates:
                    if not (entry.year or entry.month or entry.day):
                        continue
                    candidates = [EMPTY_CANDIDATE]
                    seq_start = token.start
                # Add the token to the current sequence
                candidates = self._extend(candidates, entry)
                seq_end = token.end
                # Check if there are any candidates that have year, month and day
                matches = self._build_matches(text, seq_start, seq_end, candidates)
                if matches:
                    for match in matches:
                        yield match
                    candidates = None
        # Yield any remaining matches
        for match in self._build_matches(text, seq_start, seq_end, candidates):
            yield match

    def _extract_token(self, text, token):
        token_text = text[token.start: token.end]
        if token.type == Tokenizer.LETTERS:
            token_text = token_text.lower()
        elif token.type == Tokenizer.OTHER:
            token_text = token_text.strip()
        return token_text

    def _extend(self, candidates, entry):
        new_candidates = []
        if entry.year:
            # Create new candidates by filling their year field
            new_candidates.extend((Candidate(entry.year, c.month, c.day) for c in candidates if not c.year))
        if entry.month and entry.day and self._candidates_are_empty(candidates):
            # Ambiguous entry that appears at the beginning of the sequence
            if self.month_before_day:
                new_candidates.extend((Candidate(c.year, entry.month, c.day) for c in candidates))
            else:
                new_candidates.extend((Candidate(c.year, c.month, entry.day) for c in candidates))
            return new_candidates or candidates
        if entry.month:
            # Create new candidates by filling their month field
            new_candidates.extend((Candidate(c.year, entry.month, c.day) for c in candidates if not c.month))
        if entry.day:
            # Create new candidates by filling their day field, unless there is already
            # a year and no month - because usually the day does not appear immediately after the year
            new_candidates.extend((Candidate(c.year, c.month, entry.day) for c in candidates
                                  if not c.day and not (c.year and not c.month)))
        # for c in new_candidates: print c
        return new_candidates or candidates

    def _candidates_are_empty(self, candidates):
        return candidates == [EMPTY_CANDIDATE]

    def _build_matches(self, text, start, end, candidates):
        matches = set()
        if candidates:
            for c in candidates:
                if c.year and c.month and c.day:
                    matches.add(Match(
                        date=date(c.year, c.month, c.day),
                        offset=start,
                        text=text[start : end]
                    ))
        return matches

    def _add_to_dictionary(self, token, year=None, month=None, day=None):
        token = token.lower()
        old_entry = self.entries.get(token)
        if old_entry:
            entry = Entry(
                token,
                year or old_entry.year,
                month or old_entry.month,
                day or old_entry.day
            )
        else:
            entry = Entry(token, year, month, day)
        self.entries[token] = entry

    def _build_default_dictionary(self):
        # Valueless tokens and whitespace
        for token in ',./\\-':
            self._add_to_dictionary(token)
        for n in range(1, 4):
            self._add_to_dictionary(' ' * n)
        # Years
        for year in xrange(self.min_year, self.max_year + 1):
            self._add_to_dictionary(str(year), year=year)
            self._add_to_dictionary(str(year)[2:], year=year)
        # Months
        for month in xrange(1, 13):
            self._add_to_dictionary(str(month), month=month)
            if month < 10:
                self._add_to_dictionary('0' + str(month), month=month)
        # Days
        for day in xrange(1, 32):
            self._add_to_dictionary(str(day), day=day)
            if day < 10:
                self._add_to_dictionary('0' + str(day), day=day)

    def _load_dictionary(self, name):
        from pkgutil import get_data
        text = get_data('date_detector', 'dictionaries/%s.txt' % name)
        if not text: return # FIXME
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


