import logging

logger = logging.getLogger(__name__)

from tomlkit.toml_file import TOMLFile


def parse_toml_file(filepath: str):
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


def save_toml_file(toml_doc, filepath) -> None:
    logger.info("Saving TOML file: %s", filepath)
    file = TOMLFile(filepath)
    file.write(toml_doc)
