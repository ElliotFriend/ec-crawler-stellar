import os
import requests
from github import Github
import toml

import logging
import time

# Load sensitive variables from .env
from dotenv import load_dotenv
import uuid
from github import GithubException
import re
from collections import Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("aave-ec-crawler.log"),  # Write logs to this file
        logging.StreamHandler(),  # And also print them to the console
    ],
)
load_dotenv()

# Constants and configurations
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
AAVE_TOML_URL = "https://raw.githubusercontent.com/electric-capital/crypto-ecosystems/master/data/ecosystems/a/aave.toml"
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")  # Your GitHub username
BASE_REPO = "electric-capital/crypto-ecosystems"
BRANCH_NAME = f"aave-{uuid.uuid4()}"

ORIGINAL_REPO = "electric-capital/crypto-ecosystems"
FORKED_REPO_NAME = "crypto-ecosystems"
FORKED_REPO = f"{GITHUB_USERNAME}/{FORKED_REPO_NAME}"

# Initialize GitHub API
g = Github(GITHUB_TOKEN)
user = g.get_user()
forked_repo = user.get_repo(FORKED_REPO_NAME)

logging.info("Script started. Initialized GitHub API.")


SEARCH_QUERIES = [
    {"filename": "package.json", "keyword": "aave/core-v3"},
    {"filename": "package-lock.json", "keyword": "aave/core-v3"},
    {"filename": "yarn.lock", "keyword": "aave/core-v3"},
    {"filename": "package.json", "keyword": "aave/protocol-v2"},
    {"filename": "package-lock.json", "keyword": "aave/protocol-v2"},
    {"filename": "yarn.lock", "keyword": "aave/protocol-v2"},
    {"filename": "package.json", "keyword": "aave/aave-token"},
    {"filename": "package-lock.json", "keyword": "aave/aave-token"},
    {"filename": "yarn.lock", "keyword": "aave/aave-token"},
    {"filename": "package.json", "keyword": "aave/deploy-v3"},
    {"filename": "package-lock.json", "keyword": "aave/deploy-v3"},
    {"filename": "yarn.lock", "keyword": "aave/deploy-v3"},
    {"filename": "package.json", "keyword": "aave/periphery-v3"},
    {"filename": "package-lock.json", "keyword": "aave/periphery-v3"},
    {"filename": "yarn.lock", "keyword": "aave/periphery-v3"},
    {"filename": "package.json", "keyword": "aave/safety-module"},
    {"filename": "package-lock.json", "keyword": "aave/safety-module"},
    {"filename": "yarn.lock", "keyword": "aave/safety-module"},
    {"filename": "package.json", "keyword": "aave/protocol-v2"},
    {"filename": "package-lock.json", "keyword": "aave/protocol-v2"},
    {"filename": "yarn.lock", "keyword": "aave/protocol-v2"},
    {"filename": "package.json", "keyword": "aave/governance-v2"},
    {"filename": "package-lock.json", "keyword": "aave/governance-v2"},
    {"filename": "yarn.lock", "keyword": "aave/governance-v2"},
    {"filename": "package.json", "keyword": "aave/protocol-js"},
    {"filename": "package-lock.json", "keyword": "aave/protocol-js"},
    {"filename": "yarn.lock", "keyword": "aave/protocol-js"},
    {"filename": "package.json", "keyword": "aave/contract-helpers"},
    {"filename": "package-lock.json", "keyword": "aave/contract-helpers"},
    {"filename": "yarn.lock", "keyword": "aave/contract-helpers"},
    {"filename": "package.json", "keyword": "aave/math-utils"},
    {"filename": "package-lock.json", "keyword": "aave/math-utils"},
    {"filename": "yarn.lock", "keyword": "aave/math-utils"},
    {"filename": "package.json", "keyword": "aave/aave-ui-kit"},
    {"filename": "package-lock.json", "keyword": "aave/aave-ui-kit"},
    {"filename": "yarn.lock", "keyword": "aave/aave-ui-kit"},
]


def handle_rate_limiting(response):
    if response.status_code == 403 and "rate limit exceeded" in response.text.lower():
        # Extract rate limit info from headers
        reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
        current_time = int(time.time())
        sleep_time = (
            max(reset_time - current_time, 0) + 60
        )  # Wait an extra 60 seconds beyond reset time

        logging.warning(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
        time.sleep(sleep_time)


def github_api_request(url, headers):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response
        else:
            handle_rate_limiting(response)
            return github_api_request(url, headers)  # Retry the request
    except requests.RequestException as e:
        logging.error(f"An error occurred during the GitHub API request: {e}")
        return None


def fetch_current_projects():
    """Fetch the current list of projects from aave.toml."""
    logging.info("Fetching current projects from aave.toml.")
    response = requests.get(AAVE_TOML_URL)
    data = toml.loads(response.text)
    return set([repo["url"] for repo in data["repo"]])


def build_search_query(query):
    """Build a search query string based on the given criteria."""
    query_parts = []
    if "filename" in query:
        query_parts.append(f"filename:{query['filename']}")
    if "extension" in query:
        query_parts.append(f"extension:{query['extension']}")
    if "keyword" in query:
        query_parts.append(f"{query['keyword']}")
    if "sizeRange" in query:
        query_parts.append(f"size:{query['sizeRange']}")
    if "in" in query:
        query_parts.append(f"in:{query['in']}")
    return " ".join(query_parts)


def generate_size_ranges():
    ranges = []
    start = 0

    while start < 3000:
        step = 1500
        ranges.append(f"{start}..{start + step}")
        start += step

    while start < 15000:
        step = 12000
        ranges.append(f"{start}..{start + step}")
        start += step

    return ranges


def search_new_repositories():
    """Search for new Aave-related repositories on GitHub."""
    logging.info("Starting search for new repositories.")
    size_ranges = generate_size_ranges()
    new_repos = []
    MAX_PAGE = 10
    for query in SEARCH_QUERIES:
        for sizeRange in size_ranges:
            query["sizeRange"] = sizeRange
            search_string = build_search_query(query)
            logging.info(f"Searching for {search_string}")
            page = 1
            while page <= MAX_PAGE:
                logging.info(f" * size range {sizeRange} - page [{page}/{MAX_PAGE}]")
                url = f"https://api.github.com/search/code?q={search_string}&per_page=100&page={page}"
                result = github_api_request(
                    url, {"Authorization": f"token {GITHUB_TOKEN}"}
                )  # Use the wrapper function
                data = result.json()
                items = data.get("items", [])
                if items:
                    logging.info(f"Found {len(items)} results\n")

                else:
                    logging.info("No more results\n")
                    break  # No more results

                new_repos.extend([item["repository"]["html_url"] for item in items])
                page += 1

                if len(items) < 100:
                    if page == MAX_PAGE - 1:
                        logging.warning(
                            "There may be additional repositories that match the search criteria but were not retrieved due to the GitHub API's pagination limit"
                        )
                    break  # Last page of results

    # Remove duplicates
    logging.info(f"Total found: {len(new_repos)} new repositories.")
    return set(new_repos)


def update_toml_file(existing_repos, new_repos):
    """Update the TOML file with the new repositories."""
    logging.info("Updating TOML file with new repositories.")
    new_repos_filtered = [repo for repo in new_repos if repo not in existing_repos]
    data = {"repo": [{"url": repo} for repo in existing_repos + new_repos_filtered]}
    return toml.dumps(data)


def update_toml_content(toml_content, new_repos):
    """Update the TOML content with the new repositories without overwriting existing content."""
    updated_content = toml_content.strip()  # Remove leading/trailing whitespace

    # Filter out any new repositories that already exist in the TOML content
    existing_repos = [repo["url"] for repo in toml.loads(toml_content).get("repo", [])]
    unique_new_repos = [repo for repo in new_repos if repo not in existing_repos]

    for new_repo in unique_new_repos:
        # Ensure there's a newline at the end of the existing content
        if not updated_content.endswith("\n"):
            updated_content += "\n"
        # Add the new repository entry
        new_entry = f'\n[[repo]]\nurl = "{new_repo}"'
        updated_content += new_entry

    return updated_content


def fetch_current_toml_content():
    """Fetch the current content of the TOML file from the specified URL."""
    try:
        # Send a request to the URL where the TOML file is located
        response = requests.get(AAVE_TOML_URL)

        # Raise an exception if the request was unsuccessful
        response.raise_for_status()

        # Return the content of the TOML file
        return response.text
    except requests.RequestException as e:
        logging.error(f"Failed to fetch current TOML content: {e}")
        return ""  # Return an empty string or handle this case as needed in your main script


def sync_fork_with_upstream():
    """Sync the forked repository with the upstream repository."""
    logging.info("Syncing fork with upstream repository.")

    try:
        # Get the 'master' branch from the forked repo (or 'main' if your default branch is named 'main')
        forked_master_ref = "heads/master"
        forked_master_sha = forked_repo.get_git_ref(forked_master_ref).object.sha
        # Get the latest commit from the original repository's 'master' branch
        upstream_repo = g.get_repo(ORIGINAL_REPO)
        upstream_master_sha = upstream_repo.get_branch("master").commit.sha

        # If the SHAs are different, the branches are out of sync
        if forked_master_sha != upstream_master_sha:
            # Attempt to create a merge commit
            merge_result = forked_repo.merge(base="master", head="master")

            # Check if merge_result is not None and the merge was successful
            if merge_result and getattr(merge_result, "merged", False):
                logging.info("Successfully merged upstream changes into fork.")
            else:
                logging.error(
                    "Merge failed or no merge was necessary. The fork might already be up to date."
                )
        else:
            logging.info("Fork is already up-to-date with the upstream repository.")
    except Exception as e:
        logging.error(f"An error occurred while syncing the fork: {e}")


def push_changes(updated_toml, new_repos):
    """Push changes to the forked repository and create a pull request."""
    try:
        logging.info("Pushing changes to the forked repository.")

        print(new_repos)

        # Check if 'master' branch exists in forked_repo
        if "master" not in [branch.name for branch in forked_repo.get_branches()]:
            logging.error("Master branch does not exist in the forked repository.")
            return

        # Create a new branch with the unique UUID
        ref = f"refs/heads/{BRANCH_NAME}"
        master_sha = forked_repo.get_branch("master").commit.sha
        forked_repo.create_git_ref(ref=ref, sha=master_sha)

        # Update the file in the forked repository on the new branch
        contents = forked_repo.get_contents(
            "data/ecosystems/a/aave.toml", ref=BRANCH_NAME
        )
        forked_repo.update_file(
            contents.path,
            "Update Aave project list",
            updated_toml,
            contents.sha,
            branch=BRANCH_NAME,
        )
        # Calculate the number of new projects
        new_project_count = len(new_repos)

        # Extract owner names from repository URLs and count them
        owner_pattern = re.compile(r"github\.com/([^/]+)/")
        owners = [
            owner_pattern.search(repo).group(1)
            for repo in new_repos
            if owner_pattern.search(repo)
        ]
        owner_counts = Counter(owners)

        # Sort the owners by project count
        sorted_owners = sorted(owner_counts.items(), key=lambda x: x[1], reverse=True)

        # Format the list of owners and their project counts into a markdown table
        owner_table = "| Owner | Project Count |\n| --- | --- |\n"
        owner_table += "\n".join(
            [f"| {owner} | {count} |" for owner, count in sorted_owners]
        )

        # Create a pull request in the forked repository with detailed description
        pr_body = (
            f"Updated project list with {new_project_count} new findings.\n\n"
            "## New Project Count\n"
            f"{new_project_count}\n\n"
            "## Project Owners by Project Count\n"
            f"{owner_table}"
        )

        # Create a pull request in the forked repository
        pr = forked_repo.create_pull(
            title="Update Aave Project List",
            body=pr_body,
            head=BRANCH_NAME,
            base="master",
        )
        logging.info(f"Pull request created in the forked repo: {pr.html_url}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")


def main():
    logging.info("Main function started.")
    # Sync the fork with the original repository before making changes
    sync_fork_with_upstream()

    existing_toml_content = (
        fetch_current_toml_content()
    )  # Fetch the current TOML content from the file or URL
    if not existing_toml_content:
        logging.error("Failed to fetch the current TOML content. Aborting the script.")
        return  # Exit the script or handle this case as needed

    existing_repos = fetch_current_projects()

    new_repos = search_new_repositories()
    append_repos = new_repos - existing_repos

    if append_repos:
        updated_toml_content = update_toml_content(existing_toml_content, append_repos)
        push_changes(updated_toml_content, append_repos)
    else:
        logging.info("No new repositories found. No changes made.")


if __name__ == "__main__":
    main()
