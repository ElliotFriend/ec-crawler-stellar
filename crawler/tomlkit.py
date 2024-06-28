"""
Tomlkit
-------

Abstractions to ease the reading/writing of the necessary TOML file. These
functions are wrappers around the `tomlkit` package.
"""

import logging

from tomlkit import TOMLDocument
from tomlkit.toml_file import TOMLFile

logger = logging.getLogger(__name__)


def parse_toml_file(filepath: str) -> dict:
    """Read and parse a TOML file from disk.

    :param filepath: The absolute path to the TOML file.
    :type filepath: str
    :return: A dictionary with all relevant EC-related information parsed.
    :rtype: dict
    """
    logger.info("Parsing TOML file: %s", filepath)
    file = TOMLFile(filepath)
    doc = file.read()
    sub_ecos = doc.get("sub_ecosystems")
    gh_orgs = doc.get("github_organizations")
    repo = doc.get("repo").unwrap()

    return {
        "doc": doc,
        "sub_ecos": sub_ecos,
        "gh_orgs": gh_orgs,
        "repo": repo,
    }


def save_toml_file(toml_doc: TOMLDocument, filepath: str) -> None:
    """Save the modified TOML document to disk, at filepath.

    :param toml_doc: The TOML document with additional repositories.
    :type toml_doc: TOMLDocument
    :param filepath: The absolute path where the TOML file should be saved.
    :type filepath: str
    """
    logger.info("Saving TOML file: %s", filepath)
    file = TOMLFile(filepath)
    file.write(toml_doc)
