import logging
logger = logging.getLogger(__name__)

from crawler.crawler import SEARCH_QUERIES, GITHUB_TOKEN

from github import Auth, Github
from github.GithubException import UnknownObjectException

BASE_URL: str = "https://github.com/"

auth = Auth.Token(GITHUB_TOKEN)
g = Github(auth=auth)
g.per_page = 100

def build_search_query(query: dict[str, str]) -> str:
    """Build a search query string based on the given criteria."""
    query_parts: list[str] = []

    if "filename" in query:
        query_parts.append(f"filename:{query['filename']}")
    if "path" in query:
        query_parts.append(f"path:{query['path']}")
    if "keyword" in query:
        query_parts.append(f"{query['keyword']}")

    return " ".join(query_parts)

def get_org_repos(org_url: str) -> set[str]:
    org_repos: set[str] = set()
    org_name = org_url.split('/')[-1]

    logger.info("Retrieving GH Org repos for %s", org_name)
    try:
        repos = g.get_organization(org_name).get_repos()
        for repo in repos:
            org_repos.add(f"{BASE_URL}{repo.full_name}")
    except UnknownObjectException:
        pass

    return org_repos

def search_gh_repos(ecosystem_name: str) -> set[str]:
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
