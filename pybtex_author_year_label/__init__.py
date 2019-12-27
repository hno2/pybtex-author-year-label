# -*- coding: utf-8 -*-

# Copyright (c) 2015 Chris MacMackin
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
Defines an author-year inline citation style for Pybtex. This is
modified from the alpha style built into Pybtex, written by
Andrey Golovizin.
"""

from collections import Counter
import re
from typing import List
import unicodedata

from pybtex.database import Entry, Person
from pybtex.style.labels import BaseLabelStyle

_nonalnum_pattern = re.compile(r"\W+", re.UNICODE)


def _strip_accents(s: List[str]):
    return "".join(
        (c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c))
    )


def _strip_non_alnum(parts: List[str]):
    """Strip all non-alphanumerical characters from a list of strings.

    >>> _strip_non_alnum(["ÅA. B. Testing 12+}[.@~_", u" 3%"])
    "ÅABTesting12_3"
    """
    s = "".join(parts)
    return _nonalnum_pattern.sub("", s)


def format_label_names(persons: List[Person]) -> str:
    # see alpha.bst format.lab.names
    # s = persons
    names_count = len(persons)
    if names_count > 1:
        if names_count > 2:
            names_left = 1
        else:
            names_left = names_count

        result = ""
        nameptr = 1

        while names_left:
            person = persons[nameptr - 1]
            if nameptr == names_count:
                if person == "others":
                    result += "et al. "
                else:
                    result += _strip_non_alnum(
                        person.prelast_names + [" "] + person.last()
                    )
            else:
                result += _strip_non_alnum(person.prelast_names + [" "] + person.last())
            if names_count == 2 and nameptr == 1:
                result += " and "
            else:
                result += " "
            nameptr += 1
            names_left -= 1

        if names_count > 2:
            result += "et al."
    else:
        person = persons[0]
        result = _strip_non_alnum(person.prelast_names + [" "] + person.last())
    return result


def author_key_label(entry: Entry):
    # see alpha.bst author.key.label
    if "author" in entry.persons:
        return format_label_names(entry.persons["author"])
    if "key" in entry.fields:
        # for entry.key, bst actually uses text.prefix$
        return entry.fields["key"][:]

    return entry.key[:]  # entry.key is bst cite$


def author_editor_key_label(entry: Entry):
    # see alpha.bst author.editor.key.label
    if "author" in entry.persons:
        return format_label_names(entry.persons["author"])
    if "editor" in entry.persons:
        return format_label_names(entry.persons["editor"])
    if "key" in entry.fields:
        # for entry.key, bst actually uses text.prefix$
        return entry.fields["key"][:]

    return entry.key[:]  # entry.key is bst cite$


def key_organization_label(entry: Entry):
    if "key" in entry.fields:
        return entry.fields["key"][:]
    if "organization" in entry.fields:
        result = entry.fields["organization"]
        if result.startswith("The "):
            result = result[4:]
        return result
    else:
        return entry.key[:]  # entry.key is bst cite$


def editor_key_organization_label(entry: Entry) -> str:
    if "editor" in entry.persons:
        return format_label_names(entry.persons["editor"])
    return key_organization_label(entry)


def author_key_organization_label(entry: Entry) -> str:
    if "author" in entry.persons:
        return format_label_names(entry.persons["author"])
    return key_organization_label(entry)


def format_label(entry: Entry):
    # see alpha.bst calc.label
    if entry.type in ("book", "inbook"):
        label = author_editor_key_label(entry)
    elif entry.type == "proceedings":
        label = editor_key_organization_label(entry)
    elif entry.type == "manual":
        label = author_key_organization_label(entry)
    else:
        label = author_key_label(entry)

    label = label.strip()

    if "year" in entry.fields:
        return f"{label},{entry.fields['year']}"
    else:
        return label
    # bst additionally sets sort.label


def _replace_curly_braces(label: str) -> str:
    return (
        label.replace("\\{", "&#123;")
        .replace("\\}", "&#125;")
        .replace("{", "")
        .replace("}", "")
    )


class LabelStyle(BaseLabelStyle):
    name = "author_year"

    def format_labels(self, sorted_entries):
        labels = [format_label(entry) for entry in sorted_entries]
        labels = [_replace_curly_braces(label) for label in labels]

        count = Counter(labels)
        counted = Counter()
        for label in labels:
            if count[label]:
                yield "(" + label + ")"
            else:
                yield "(" + label + chr(ord("a") + counted[label]) + ")"
                counted.update([label])
