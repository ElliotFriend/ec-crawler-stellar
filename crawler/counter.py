"""
Counter
-------

Take a stab at actually counting the repos/contributors in the ecosystem.
"""

import logging
from operator import itemgetter

from crawler.constants import BASE_REPO_PATH
from crawler.ecosystem import parse_eco_filename
from crawler.search_github import get_contributors, get_org_repos
from crawler.tomlkit import parse_toml_file

logger = logging.getLogger(__name__)


def get_ecosystem_repos(ecosystem_name: str) -> dict[str, set[str]]:
    """Retrieve the tracked repos in the given ecosystem.

    :param ecosystem_name: The name of the ecosystem, as written in an EC TOML
        file.
    :type ecosystem_name: str
    """
    ecosystem_sets: dict[str, set[str]] = {ecosystem_name: set()}
    ecosystem = parse_eco_filename(ecosystem_name)
    filepath: str = f"{BASE_REPO_PATH}/data/ecosystems/{ecosystem[0]}/{ecosystem}.toml"

    # 0. load/parse the TOML
    sub_ecos: list[str]
    gh_orgs: list[str]
    repos: list[dict[str, str]]

    sub_ecos, gh_orgs, repos = itemgetter("sub_ecos", "gh_orgs", "repos")(
        parse_toml_file(filepath)
    )

    ecosystem_sets[ecosystem_name].update(
        r["url"].lower() for r in repos if not "missing" in r
    )

    # 1. recurse into the subecosystems
    if len(sub_ecos):
        for sub_eco in sub_ecos:
            sub_repos = get_ecosystem_repos(sub_eco)
            ecosystem_sets[sub_eco] = sub_repos[sub_eco]

    logger.info("Retrieving repositories in ecosystem: %s", ecosystem)

    # 2. add github org repos
    for org in gh_orgs:
        org_repos = get_org_repos(org)
        ecosystem_sets[ecosystem_name].update(r.lower() for r in org_repos)

    # 3. log the findings
    logger.info(
        "Tracking %d repositories in the %s ecosystem.",
        len(ecosystem_sets[ecosystem_name]),
        ecosystem_name,
    )

    # 4. return the sets, so it can be combined/grand-totalled
    return ecosystem_sets


def count_all_repos(parent_ecosystem: str) -> None:
    """Count the tracked repos from the parent ecosystem, including all
    sub-ecosystems.
    """
    logger.info("Counting all repos in the parent ecosystem: %s", parent_ecosystem)
    all_sets = get_ecosystem_repos(parent_ecosystem)
    all_repos: set[str] = set()

    for repos in all_sets.values():
        all_repos.update(repos)

    logger.info(
        "Tracking %d repositories across the entire %s parent ecosystem.",
        len(all_repos),
        parent_ecosystem,
    )


def get_ecosystem_contributors(ecosystem_name: str) -> dict[str, set[str]]:
    """Count all contributors to the tracked repos from the previous 30 days."""

    contributor_sets: dict[str, set[str]] = {ecosystem_name: set()}

    ecosystem_repos_sets = get_ecosystem_repos(ecosystem_name)

    for eco, repos in ecosystem_repos_sets.items():
        logger.info("Counting contributors for ecosystem: %s", eco)
        contributors = get_contributors(repos)
        contributor_sets[eco] = contributors
        logger.info(
            "Found %d recent contributors in the %s ecosystem", len(contributors), eco
        )

    return contributor_sets


def count_all_contributors(parent_ecosystem: str) -> None:
    """Count the contributors for all the tracked repos from the parent
    ecosystem, including all sub-ecosystems.
    """
    logger.info(
        "Counting all contributors in the parent ecosystem: %s", parent_ecosystem
    )
    all_sets = get_ecosystem_contributors(parent_ecosystem)
    all_contributors: set[str] = set()

    for repos in all_sets.values():
        all_contributors.update(repos)

    logger.info(
        "Found %d recent contributors across the entire %s parent ecosystem.",
        len(all_contributors),
        parent_ecosystem,
    )
