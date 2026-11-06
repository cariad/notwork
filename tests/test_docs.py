from functools import cache
from importlib import import_module
from os import PathLike
from pathlib import Path
from pkgutil import iter_modules
from re import sub
from tomllib import loads
from typing import Any, NamedTuple

from pytest import mark, param

ROOT = Path(__file__).parent.parent
DOCS = Path("docs")


class Section(NamedTuple):
    """A module whose exports are documented, and where its documentation lives."""

    directory: str
    module: str
    navigation: str


SECTIONS = [
    Section(
        directory="functions",
        module="notwork",
        navigation="Functions",
    ),
    Section(
        directory="models",
        module="notwork.models",
        navigation="Models",
    ),
    Section(
        directory="exceptions",
        module="notwork.exceptions",
        navigation="Exceptions",
    ),
]

PACKAGE = "notwork"
"""The root package, which re-exports every subpackage's exports for consumers."""

CONSTANTS = "notwork.constants"
"""Package whose modules group related constants, each documented on one page."""

SUBPACKAGES = [
    "notwork.exceptions",
    "notwork.models",
    CONSTANTS,
]
"""Subpackages whose exports the root package re-exports."""

SUBPACKAGE_EXPORTS = [
    param(module, name, id=f"{module}.{name}")
    for module in SUBPACKAGES
    for name in import_module(module).__all__
]

REEXPORTS = {name for module in SUBPACKAGES for name in import_module(module).__all__}
"""Names that the root package re-exports, and which are documented elsewhere."""

EXPORTS = [
    param(section, name, id=f"{section.module}.{name}")
    for section in SECTIONS
    for name in import_module(section.module).__all__
    if section.module != PACKAGE or name not in REEXPORTS
]

CONSTANT_MODULES = [
    param(info.name, id=f"{CONSTANTS}.{info.name}")
    for info in iter_modules(import_module(CONSTANTS).__path__)
]

CONSTANT_EXPORTS = [
    param(name, id=f"{CONSTANTS}.{name}") for name in import_module(CONSTANTS).__all__
]


def _snake_case(name: str) -> str:
    """Convert a name like `PortOutOfRangeError` to `port_out_of_range_error`."""
    return sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name).lower()


def _module(section: Section, name: str) -> str:
    """The module that an export must be defined in, named after it in snake case."""
    return f"{section.module}.{_snake_case(name)}"


def _page(section: Section, name: str) -> str:
    """The path to an export's page, relative to the documentation's directory."""
    return f"{section.directory}/{_snake_case(name)}.md"


def _read(path: PathLike[str] | str) -> str:
    """Read a file, given its path relative to the repository."""
    return (ROOT / path).read_text(encoding="utf-8")


@cache
def _nav() -> list[dict[str, Any]]:
    """The site's navigation, read from `zensical.toml` once and reused."""
    return loads(_read("zensical.toml"))["project"]["nav"]


@mark.parametrize(
    ("module", "name"),
    SUBPACKAGE_EXPORTS,
)
def test_package_reexports_subpackage_export(module: str, name: str) -> None:
    """Assert that the root package re-exports a subpackage's export."""
    package = import_module(PACKAGE)

    assert name in package.__all__
    assert getattr(package, name) is getattr(import_module(module), name)


@mark.parametrize(
    ("section", "name"),
    EXPORTS,
)
def test_export_is_defined_in_its_own_module(section: Section, name: str) -> None:
    """Assert that an export is defined in a module named after it, in snake case."""
    export = getattr(import_module(section.module), name)
    defined_in: str | None = getattr(export, "__module__", None)
    expect = _module(section, name)

    assert defined_in == expect


@mark.parametrize(
    ("section", "name"),
    EXPORTS,
)
def test_navigation_lists_export(section: Section, name: str) -> None:
    """Assert that the site's navigation links to an export's page."""
    nav = _nav()

    # A missing section has no entries, so the assertion below fails and shows why.
    missing: list[dict[str, str]] = []

    entries = next(
        (entry[section.navigation] for entry in nav if section.navigation in entry),
        missing,
    )

    expect = {
        name: _page(section, name),
    }

    assert expect in entries


@mark.parametrize(
    ("section", "name"),
    EXPORTS,
)
def test_page_documents_export(section: Section, name: str) -> None:
    """Assert that an export has a reference page that documents it."""
    page = _read(DOCS / _page(section, name))
    expect = f"::: {_module(section, name)}.{name}\n"

    assert page.startswith(expect)


@mark.parametrize(
    "name",
    CONSTANT_EXPORTS,
)
def test_constant_is_defined_in_a_constants_module(name: str) -> None:
    """Assert that an exported constant comes from a documented constants module."""
    value = getattr(import_module(CONSTANTS), name)

    defined_in = [
        info.name
        for info in iter_modules(import_module(CONSTANTS).__path__)
        if getattr(import_module(f"{CONSTANTS}.{info.name}"), name, None) is value
    ]

    assert len(defined_in) == 1


@mark.parametrize(
    "module",
    CONSTANT_MODULES,
)
def test_navigation_lists_constants_module(module: str) -> None:
    """Assert that the site's navigation links to a constants module's page."""
    nav = _nav()

    # A missing section has no entries, so the assertion below fails and shows why.
    missing: list[dict[str, str]] = []

    entries = next(
        (entry["Constants"] for entry in nav if "Constants" in entry),
        missing,
    )

    pages = [page for entry in entries for page in entry.values()]

    assert f"constants/{module}.md" in pages


@mark.parametrize(
    "module",
    CONSTANT_MODULES,
)
def test_page_documents_constants_module(module: str) -> None:
    """Assert that a constants module has a reference page that documents it."""
    page = _read(DOCS / f"constants/{module}.md")
    expect = f"::: {CONSTANTS}.{module}\n"

    assert page.startswith(expect)
