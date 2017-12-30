Overview
========
The purpose of this module is to efficiently find dates inside text, in almost any format. For example:

```python
text = """
                         24/5/2017
   Dear Morty,
   I will be visiting New York between December 22nd, 2017 and January 1, 2018.
   Yours,
   Ben
"""

from date_detector import Parser
parser = Parser()
for match in parser.parse(text):
     print(match)

>>> Match(date=datetime.date(2017, 5, 24), offset=26, text='24/5/2017')
>>> Match(date=datetime.date(2017, 12, 22), offset=90, text='December 22nd, 2017')
>>> Match(date=datetime.date(2018, 1, 1), offset=114, text='January 1, 2018')
```

How does it work?
-----------------
The text is broken up into tokens, which are sequences of characters from a single type: digits, letters, whitespace or other. The algorithm then tries to find sequences of tokens which might be a part of a date, for example `2017`, `09` or `December`. Any sequence that can be interpreted as a valid date is returned. Some sequences can be interpreted as as several different dates, in which case they are all returned (for example: `01/02/03`).

Similar projects
----------------
* datefinder (https://github.com/akoumjian/datefinder)
* dateparser (https://github.com/scrapinghub/dateparser)
* date-extractor (https://github.com/DanielJDufour/date-extractor)
* parsedatetime (https://github.com/bear/parsedatetime)
* python-natty (https://github.com/eadmundo/python-natty)

Usage
=====
To look for dates in a text, first construct a `Parser`:
```python
from date_detector import Parser
parser = Parser()
```
Then use the `parse` method to get a generator returning `Match` objects. Each match has three fields: `date`, `offset`, and `text`.
```python
for match in parser.parse(text):
    # Do something with match.date
```
Parser options
--------------
When constructing a `Parser` instance, you can pass several options:
* `dictionaries`: a list of language codes of dictionaries to use (default: ["en"]). See below for more information about dictionaries.
* `month_before_day`: whether to prefer M/D/Y dates (American) over D/M/Y (default: `False`).
* `min_date`: the minimal date to consider (default: 1950-01-01).
* `max_date`: the maximal date to consider (default: 2049-12-31).
* `tokenizer_class`: the class to use for tokenizing text (default: `Tokenizer`)

Language Dictionaries
---------------------
Currently the following languages are supported:
* English (en)
* Hebrew (he)

To support additional languages, dictionary files need to be added. They should be located under the `date_detector/dictionaries` directory. Take a look at the existing dictionaries to see how they are formatted.

Note: dictionaries are case-insensitive.

Contributing
============
After checking out the code, build the project by running the following commands:

    easy_install -U infi.projector
    projector devenv build --use-isolated-python

Running tests
-------------
To run the tests:

    cd src
    ../bin/nosetests

