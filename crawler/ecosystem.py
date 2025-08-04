"""
Ecosystem
---------

The main workhorse of the package! This module is responsible for managing the
process of the crawl.
"""

import json
import logging
import shlex
import subprocess
from datetime import datetime
from os import getcwd
from typing import TypedDict

from crawler.constants import BASE_ECOSYSTEM, BASE_REPO_PATH
from crawler.search_github import search_gh_repos

logger = logging.getLogger(__name__)


class RepoJson(TypedDict):
    eco_name: str
    branch: list[str]
    repo_url: str
    tags: list[str]


def parse_eco_filename(ecosystem_name: str) -> str:
    """Parse the provided ecosystem name into a filepath-like string.

    :param ecosystem_name: The name of the ecosystem, as written in the EC
        taxonomy DSL mutations.
    :type ecosystem_name: str
    :return: A filepath-friendly string of the ecosystem name.
    :rtype: str
    """
    return "-".join(ecosystem_name.split()).lower().replace("(", "").replace(")", "")


def run_export_ecosystem(ecosystem_name: str) -> list[RepoJson]:
    """Export the jsonl file for the ecosystem and return it as a list

    :param ecosystem_name: The name of the ecosystem, as written in the EC
        taxonomy DSL mutations.
    :type ecosystem_name: str
    :return: The exported taxonomy of repositories, as a list of typed dicts.
    :rtype: list[RepoJson]
    """
    ecosystem = parse_eco_filename(ecosystem_name)
    filepath: str = f"{getcwd()}/out/{ecosystem}.jsonl"

    command = shlex.split(
        f'./run.sh export -e "{ecosystem_name}" {filepath}'
        # f'./run.sh export -e "{ecosystem_name}" -m 2025-04-01 {filepath}'
    )
    p = subprocess.Popen(command, cwd=BASE_REPO_PATH)
    p.wait()

    with open(filepath, "r") as file:
        repos_list: list[RepoJson] = [json.loads(l) for l in list(file)]

    return repos_list


def find_sub_ecosystems(repos_list: list[RepoJson]) -> set[str]:
    """Find the unique sub-ecosystems in an ecosystem's taxonomy file.

    :param repos_list: The list of all repos in an ecosystem.
    :type repos_list: list[RepoJson]
    :return: The unique "branches" for all the ecosystem's repos.
    :rtype: set[str]
    """
    return set(branch for repo in repos_list for branch in repo["branch"])


def process_ecosystem(ecosystem_name: str, is_sub_eco: bool = False) -> None:
    """Process the ecosystem, managing the entire process.

    :param ecosystem_name: The name of the ecosystem, as written in the EC
        taxonomy DSL mutations.
    :type ecosystem_name: str
    """
    ecosystem_repos: set[str] = set()
    ecosystem = parse_eco_filename(ecosystem_name)

    # 0. export the jsonl file for the ecosystem and read/load it for use here
    repos_list = run_export_ecosystem(ecosystem_name)
    current_repos: set[str] = set(r["repo_url"] for r in repos_list)

    # 1. recurse into subecosystems
    branches = find_sub_ecosystems(repos_list)

    for branch in branches:
        process_ecosystem(ecosystem_name=branch, is_sub_eco=True)

    logger.info("Processing ecosystem: %s", ecosystem)

    # 1. add search results
    found_repos = search_gh_repos(ecosystem)
    ecosystem_repos.update(found_repos)

    # 2. Check if there are any new repos to add to the taxonomy.
    new_repos = ecosystem_repos.difference(current_repos)
    if len(new_repos) == 0:
        logger.info("No new repositories found")
        return

    # 3. sort and add new_repos to a taxonomy mutation, save to disk
    logger.info("Found %d new repositories.", len(new_repos))
    repo_list = list(new_repos)
    mutation_filepath = f"{BASE_REPO_PATH}/migrations/{datetime.today().strftime('%Y-%m-%d')}T235959_{BASE_ECOSYSTEM}_mutations"
    use_quotes = " " in ecosystem_name
    quoted_ecosystem_name = (
        f"{"\"" if use_quotes else ""}{ecosystem_name}{"\"" if use_quotes else ""}"
    )
    logger.info("quoted_ecosystem_name: %s", quoted_ecosystem_name)

    with open(mutation_filepath, "a+") as f:
        for repo in repo_list:
            # the DSL looks like: `repadd "Aquarius (AQUA token)" https://github.com/AquaToken/aqua-airdrop-checker`
            dsl_text = f"repadd {quoted_ecosystem_name} {repo}"
            f.write("%s\n" % dsl_text)
