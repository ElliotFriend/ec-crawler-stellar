"""
Github
------

This module is primarily concerned with Github-related matters. We retrieve all
of an org's public repositories, build search queries from the defined
`SEARCH_QUERIES` dictionary in `crawler.py`, and page through code search
results.
"""

import logging

from github import Auth, Github
from github.GithubException import UnknownObjectException

from crawler.constants import SEARCH_QUERIES, GITHUB_TOKEN

logger = logging.getLogger(__name__)

BASE_URL: str = "https://github.com/"

auth = Auth.Token(GITHUB_TOKEN)
g = Github(auth=auth)
g.per_page = 100


def build_search_query(query: dict[str, str]) -> str:
    """Build a search query string based on the given criteria.

    :param query: The dictionary of query qualifiers, keyed by available `Github
        API search query qualifiers`_
    :type query: dict[str, str]
    :return: The formatted query string to use in the Github search request.
    :rtype: str

    _Github API search query qualifiers:
        https://docs.github.com/search-github/searching-on-github/searching-code
    """
    query_parts: list[str] = []

    if "filename" in query:
        query_parts.append(f"filename:{query['filename']}")
    if "path" in query:
        query_parts.append(f"path:{query['path']}")
    if "keyword" in query:
        query_parts.append(f"{query['keyword']}")

    return " ".join(query_parts)


def get_org_repos(org_url: str) -> set[str]:
    """Retrieve all of a Github organization's public repositories.

    :param org_url: The full URL of a Github organization.
    :type org_url: str
    :return: A set of unique repository URLs belonging to the Github
        organization.
    :rtype: set[str]
    """
    org_repos: set[str] = set()
    org_name = org_url.split("/")[-1]

    logger.info("Retrieving GH Org repos for %s", org_name)
    try:
        repos = g.get_organization(org_name).get_repos()
        for repo in repos:
            org_repos.add(f"{BASE_URL}{repo.full_name}")
    except UnknownObjectException:
        pass

    return org_repos


def search_gh_repos(ecosystem_name: str) -> set[str]:
    """Use Github's code search API to find repositories in the ecosystem.

    :param ecosystem_name: The name of the ecosystem to find repositories for.
    :type ecosystem_name: str
    :return: A set of unique repository URLs
    :rtype: set[str]
    """
    found_repos: set[str] = set()

    if ecosystem_name in SEARCH_QUERIES:
        for query in SEARCH_QUERIES[ecosystem_name]:
            search = build_search_query(query)
            logger.info("Searching for %s", search)
            code_results = g.search_code(search)
            logger.info("Found %d code results", code_results.totalCount)
            for res in code_results:
                found_repos.add(res.repository.html_url)

    return found_repos
