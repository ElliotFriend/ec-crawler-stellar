"""
Counter
-------

Take a stab at actually counting the repos/contributors in the ecosystem.
"""

import logging
from os import getcwd

from crawler.constants import BASE_REPO_PATH
from crawler.ecosystem import parse_eco_filename, run_export_ecosystem, find_sub_ecosystems
from crawler.search_github import get_contributors

logger = logging.getLogger(__name__)


def get_ecosystem_repos(ecosystem_name: str) -> dict[str, set[str]]:
    """Retrieve the tracked repos in the given ecosystem.

    :param ecosystem_name: The name of the ecosystem, as written in the EC
        taxonomy DSL mutations.
    :type ecosystem_name: str
    """
    ecosystem_sets: dict[str, set[str]] = {ecosystem_name: set()}
    ecosystem = parse_eco_filename(ecosystem_name)

    repos_list = run_export_ecosystem(ecosystem_name)

    # 1. recurse into the subecosystems
    sub_ecos = find_sub_ecosystems(repos_list)
    if len(sub_ecos):
        for sub_eco in sub_ecos:
            sub_repos = get_ecosystem_repos(sub_eco)
            ecosystem_sets[sub_eco] = sub_repos[sub_eco]

    logger.debug("Retrieving repositories in ecosystem: %s", ecosystem)
    existing_repos: set[str] = set()
    for repos in ecosystem_sets.values():
        existing_repos.update(repos)
    ecosystem_sets[ecosystem_name].update(
        r["repo_url"] for r in repos_list if r["repo_url"] not in existing_repos
    )

    # 2. log the findings
    logger.info(
        "Tracking %d repositories in the %s ecosystem.",
        len(ecosystem_sets[ecosystem_name]),
        ecosystem_name,
    )

    # 3. store the findings
    out_filepath: str = f"{getcwd()}/out/dumps/repos/{ecosystem}.txt"
    with open(out_filepath, "w") as f:
        f.writelines(f"{repo}\n" for repo in ecosystem_sets[ecosystem_name])

    # 3. return the sets, so it can be combined/grand-totalled
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

        out_filepath: str = f"{getcwd()}/out/dumps/contribs/{eco}.txt"
        with open(out_filepath, "w") as f:
            f.writelines(f"{contrib}\n" for contrib in contributors)

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

    for contributors in all_sets.values():
        all_contributors.update(contributors)

    logger.info(
        "Found %d recent contributors across the entire %s parent ecosystem.",
        len(all_contributors),
        parent_ecosystem,
    )
