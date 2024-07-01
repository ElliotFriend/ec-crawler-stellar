"""
Ecosystem
---------

The main workhorse of the package! This module is responsible for managing the
process of the crawl.
"""

import logging
from operator import itemgetter

from crawler.constants import BASE_REPO_PATH
from crawler.search_github import get_org_repos, search_gh_repos
from crawler.tomlkit import parse_toml_file, save_toml_file

logger = logging.getLogger(__name__)


def parse_eco_filename(ecosystem_name: str) -> str:
    """Parse the provided ecosystem name into a filepath-like string.

    :param ecosystem_name: The name of the ecosystem, as written in an EC TOML
        file.
    :type ecosystem_name: str
    :return: A filepath-friendly string of the ecosystem name..
    :rtype: str
    """
    return "-".join(ecosystem_name.split()).lower().replace("(", "").replace(")", "")


def process_ecosystem(ecosystem_name: str) -> None:
    """Process the ecosystem, managing the entire process.

    :param ecosystem_name: The name of the ecosystem, as written in an EC TOML
        file.
    :type ecosystem_name: str
    """
    ecosystem_repos: set[str] = set()
    ecosystem = parse_eco_filename(ecosystem_name)
    filepath: str = f"{BASE_REPO_PATH}/data/ecosystems/{ecosystem[0]}/{ecosystem}.toml"

    # 0. load/parse the TOML
    doc, sub_ecos, gh_orgs, repo = itemgetter("doc", "sub_ecos", "gh_orgs", "repo")(
        parse_toml_file(filepath)
    )
    current_repos: set[str] = set(r["url"] for r in repo)

    # 1. recurse into subecosystems
    for sub_eco in sub_ecos:
        process_ecosystem(sub_eco)

    logger.info("Processing ecosystem: %s", ecosystem)

    # 2. add github org repos
    for org in gh_orgs:
        org_repos = get_org_repos(org)
        ecosystem_repos.update(org_repos)

    # 3. add search results
    found_repos = search_gh_repos(ecosystem)
    ecosystem_repos.update(found_repos)

    # 4. Check if there are any new repos to add to the toml file.
    new_repos = ecosystem_repos.difference(current_repos)
    if len(new_repos) == 0:
        logger.info("No new repositories found")
        return

    # 4. sort and add new_repos to toml repo, save to disk
    logger.info("Found %d new repositories.", len(new_repos))
    repo_list = list({"url": r} for r in new_repos)
    repo.extend(repo_list)
    repo.sort(key=lambda x: x["url"].lower())
    doc.update({"repo": repo})
    save_toml_file(doc, filepath)
