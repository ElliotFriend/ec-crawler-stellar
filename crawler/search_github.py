"""
Search Github
-------------

This module is primarily concerned with Github-related matters. We retrieve all
of an org's public repositories, build search queries from the defined
`SEARCH_QUERIES` dictionary in `constants.py`, and page through code search
results.
"""

import datetime
import logging
from datetime import timedelta

from github import Auth, Github, GithubException
from github.GithubException import UnknownObjectException

from crawler.constants import BASE_GITHUB_URL, GITHUB_TOKEN, SEARCH_QUERIES

logging.getLogger("github.Requester").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

auth = Auth.Token(GITHUB_TOKEN) if GITHUB_TOKEN else None
g = Github(auth=auth)
g.per_page = 100


def build_search_query(query: dict[str, str]) -> str:
    """Build a search query string based on the given criteria.

    :param query: The dictionary of query qualifiers, keyed by available Github
        `API search query qualifiers
        <https://docs.github.com/search-github/searching-on-github/searching-code>`_
    :type query: dict[str, str]
    :return: The formatted query string to use in the Github search request.
    :rtype: str
    """
    query_parts: list[str] = []

    if "filename" in query:
        query_parts.append(f"filename:{query['filename']}")
    if "path" in query:
        query_parts.append(f"path:{query['path']}")
    if "keyword" in query:
        query_parts.append(f"{query['keyword']}")

    query_parts.append("sort:updated")
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
            org_repos.add(f"{BASE_GITHUB_URL}{repo.full_name}")
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
        logger.info("Searching code in the %s ecosystem", ecosystem_name)
        for query in SEARCH_QUERIES[ecosystem_name]:
            search = build_search_query(query)
            logger.debug("Searching for %s", search)
            code_results = g.search_code(search)
            logger.debug("Found %d code results", code_results.totalCount)
            for res in code_results:
                found_repos.add(res.repository.html_url)

    return found_repos


def get_contributors(ecosystem_repos_set: set[str]) -> set[str]:
    """Use Github's commit search API to find contributors to the repos

    :param ecosystem_repos_set: The set of unique repos for the ecosystem.
    :type ecosystem_repos_set: set[str]
    :return: A set of unique Github usernames
    :rtype: set[str]
    """
    contributors: set[str] = set()
    for repo in ecosystem_repos_set:
        project = repo.split("/")[-1]
        owner = repo.split("/")[-2]

        try:
            now = datetime.datetime.now(datetime.timezone.utc)
            repository = g.get_repo(f"{owner}/{project}")
            if (
                not repository.archived
                and now - timedelta(days=28) <= repository.updated_at <= now
            ):
                commits = repository.get_commits(
                    since=datetime.datetime.now() - timedelta(days=28),
                    until=datetime.datetime.now(),
                )
                for commit in commits:
                    if commit.author:
                        committer = commit.author.login or commit.author.name
                    elif commit.commit.author:
                        committer = commit.commit.author.name
                    else:
                        print(f"weird nonetype thing? {commit.html_url}")
                        continue

                    if committer and "[bot]" not in committer:
                        contributors.add(committer.lower())
        except UnknownObjectException as err:
            logger.exception(
                "GithubException.UnknownObjectException encountered: %s", err
            )
        except GithubException as err:
            if err.status == 409:
                logger.exception(
                    "GithubException %d encountered (probably an empty repo): %s",
                    409,
                    err,
                )
            else:
                logger.exception("GithubException encountered: %s", err)

    return contributors
