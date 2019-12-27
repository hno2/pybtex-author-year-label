from typing import List
from unittest.mock import Mock

from pybtex.database import Entry, Person
from pybtex_author_year_label import (
    _replace_curly_braces,
    _strip_non_alnum,
    author_editor_key_label,
    author_key_label,
    author_key_organization_label,
    editor_key_organization_label,
    format_label_names,
    key_organization_label,
)
import pytest


@pytest.fixture()
def format_label_names_mock(mocker) -> Mock:
    return mocker.patch("pybtex_author_year_label.format_label_names")


@pytest.fixture()
def key_organization_label_mock(mocker) -> Mock:
    return mocker.patch("pybtex_author_year_label.key_organization_label")


@pytest.fixture()
def key_field():
    return {"key": "demo-entry"}


@pytest.fixture()
def author():
    return {"author": [Person(last="Einstein")]}


@pytest.fixture()
def editor():
    return {"editor": [Person(last="Perkins")]}


@pytest.fixture()
def organization():
    return {"organization": "Python Foundation"}


@pytest.mark.parametrize(
    "parts,expected", [(["ÅA. B. Testing 12+}[.@~_", u" 3%"], "ÅABTesting12_3")]
)
def test_strip_noalnum(parts: List[str], expected: str):
    assert _strip_non_alnum(parts) == expected


@pytest.mark.parametrize(
    "label,expected",
    [
        ("abc", "abc"),
        ("\\{abc", "&#123;abc"),
        ("abc\\}", "abc&#125;"),
        ("\\{abc\\}", "&#123;abc&#125;"),
        ("{abc", "abc"),
        ("abc}", "abc"),
        ("{abc}", "abc"),
        ("\\{{abc}\\}", "&#123;abc&#125;"),
    ],
)
def test_replace_curly_braces(label: str, expected: str):
    assert _replace_curly_braces(label) == expected


@pytest.mark.parametrize(
    "entry,expected",
    [
        # Single person
        ([Person(prelast="A.", last="Einstein")], "AEinstein"),
        # Two persons
        ([Person(last="Einstein"), Person(last="Curie")], "Einstein and Curie "),
        # More than two persons
        (
            [Person(last="Curie"), Person(last="Einstein"), Person("Nobel")],
            "Curie et al.",
        ),
    ],
)
def test_format_label_names(entry: List[Person], expected: str):
    actual = format_label_names(entry)
    assert actual == expected


def test_author_key_label__with_author_and_key(key_field, author):
    entry = Entry("misc", persons=author, fields=key_field)

    actual = author_key_label(entry)
    assert actual == "Einstein"


def test_author_key_label__with_key_in_fields(key_field):
    entry = Entry("misc", fields=key_field)

    actual = author_key_label(entry)
    assert actual == "demo-entry"


def test_author_key_label__with_key():
    entry = Entry("misc")
    entry.key = "demo-key"

    actual = author_key_label(entry)
    assert actual == "demo-key"


def test_author_editor_key_label__with_author_editor_and_key(key_field, author, editor):
    persons = author
    persons.update(editor)
    entry = Entry("misc", persons=persons, fields=key_field)

    actual = author_editor_key_label(entry)
    assert actual == "Einstein"


def test_author_editor_key_label__with_editor_and_key(key_field, editor):
    entry = Entry("misc", persons=editor, fields=key_field)

    actual = author_editor_key_label(entry)
    assert actual == "Perkins"


def test_author_editor_key_label__with_key_in_fields(key_field):
    entry = Entry("misc", fields=key_field)

    actual = author_editor_key_label(entry)
    assert actual == "demo-entry"


def test_author_editor_key_label__with_key():
    entry = Entry("misc")
    entry.key = "demo-key"

    actual = author_editor_key_label(entry)
    assert actual == "demo-key"


def test_key_organization_label__with_key_and_organization(organization, key_field):
    key_field.update(organization)
    entry = Entry("misc", fields=key_field)

    actual = key_organization_label(entry)
    assert actual == "demo-entry"


@pytest.mark.parametrize(
    "organization_name,expected",
    [
        ("Python Foundation", "Python Foundation"),
        ("The Python Foundation", "Python Foundation"),
    ],
)
def test_key_organization_label__with_organization(organization_name, expected):
    entry = Entry("misc", fields={"organization": organization_name})

    actual = key_organization_label(entry)
    assert actual == expected


def test_editor_key_organization_label__with_editor(format_label_names_mock, editor):
    # Arrange
    format_label_names_mock.return_value = "Perkins"

    entry = Entry("misc", persons=editor)
    actual = editor_key_organization_label(entry)

    # Act
    format_label_names_mock.assert_called_once_with(editor["editor"])

    # Assert
    assert actual == "Perkins"


def test_editor_key_organization_label__without_editor(
    key_organization_label_mock, key_field
):
    # Arrange
    key_organization_label_mock.return_value = "demo-entry"

    entry = Entry("misc", fields=key_field)
    actual = editor_key_organization_label(entry)

    # Act
    key_organization_label_mock.assert_called_once_with(entry)

    # Assert
    assert actual == "demo-entry"


def test_author_key_organization_label__with_author(format_label_names_mock, author):
    # Arrange
    format_label_names_mock.return_value = "Einstein"

    entry = Entry("misc", persons=author)
    actual = author_key_organization_label(entry)

    # Act
    format_label_names_mock.assert_called_once_with(author["author"])

    # Assert
    assert actual == "Einstein"


def test_author_key_organization_label__without_author(
    key_organization_label_mock, key_field
):
    # Arrange
    key_organization_label_mock.return_value = "demo-entry"

    entry = Entry("misc", fields=key_field)
    actual = author_key_organization_label(entry)

    # Act
    key_organization_label_mock.assert_called_once_with(entry)

    # Assert
    assert actual == "demo-entry"
