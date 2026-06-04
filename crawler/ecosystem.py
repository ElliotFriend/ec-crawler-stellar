"""
Ecosystem
---------

The main workhorse of the package! This module is responsible for managing the
process of the crawl.
"""

import json
import logging
import os
import shlex
import subprocess
from datetime import datetime
from typing import TypedDict

from crawler.constants import BASE_ECOSYSTEM, BASE_REPO_PATH
from crawler.search_github import search_gh_repos

logger = logging.getLogger(__name__)


class RepoJson(TypedDict):
    """A dictionary representing each repo in the EC taxonomy."""

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
    filepath: str = f"{os.getcwd()}/out/{ecosystem}.jsonl"

    command = shlex.split(
        f'./run.sh export -e "{ecosystem_name}" {filepath}'
        # f'./run.sh export -e "{ecosystem_name}" -m 2025-04-01 {filepath}'
    )

    # Open Dev Data's `run.sh` runs the CLI directly when it detects an active
    # virtualenv (`VIRTUAL_ENV`), otherwise it falls back to `uv run`. When this
    # crawler is launched via `poetry run`, `VIRTUAL_ENV` points at the crawler's
    # own venv -- which does NOT have the `open-dev-data` CLI installed -- so the
    # export would fail. Strip it from the subprocess env to force the `uv run`
    # path, which resolves the CLI from the Open Dev Data project itself.
    env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    result = subprocess.run(command, cwd=BASE_REPO_PATH, env=env, check=False)
    if result.returncode != 0:
        # Fail loudly rather than silently reading a stale export from a previous
        # run, which would make the crawler operate on outdated taxonomy data.
        raise RuntimeError(
            f"Taxonomy export failed (exit {result.returncode}) for "
            f"ecosystem '{ecosystem_name}'. Is `uv` installed and is "
            f"BASE_REPO_PATH a valid Open Dev Data clone?"
        )

    with open(filepath, "r", encoding="utf-8") as file:
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


def write_repadd_mutations(ecosystem_name: str, repos: list[str]) -> str:
    """Append `repadd` lines for the given repos to today's mutation file.

    :param ecosystem_name: The ecosystem to attribute the repos to, as written
        in the Open Dev Data taxonomy DSL.
    :param repos: The repository URLs to add.
    :return: The path of the mutation file that was written.
    """
    mutation_name = f"{datetime.today().strftime('%Y-%m-%d')}T235959_{BASE_ECOSYSTEM}"
    mutation_filepath = f"{BASE_REPO_PATH}/migrations/{mutation_name}_mutations"

    # the DSL quotes ecosystem names containing spaces, e.g.
    # `repadd "Aquarius (AQUA token)" https://github.com/...`
    name = f'"{ecosystem_name}"' if " " in ecosystem_name else ecosystem_name

    with open(mutation_filepath, "a+", encoding="utf-8") as f:
        for repo in repos:
            f.write(f"repadd {name} {repo}\n")

    return mutation_filepath


def process_ecosystem(ecosystem_name: str) -> None:
    """Process the ecosystem, managing the entire process.

    :param ecosystem_name: The name of the ecosystem, as written in the Open Dev
        Data taxonomy DSL mutations.
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
        process_ecosystem(ecosystem_name=branch)

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
    mutation_filepath = write_repadd_mutations(ecosystem_name, sorted(new_repos))
    logger.info("Wrote mutations to %s", mutation_filepath)
