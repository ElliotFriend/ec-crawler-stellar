"""
Crawler
-------

The entry point of the package! Here, we grab the Github token, defined the base
(or 'starting') ecosystem we'll crawl, configure logging, and make sure the user
is ready to go.

Then, user will be presented with a 'hey, don't forget to make a new branch'
kind-of message. After confirming, the `process_ecosystem()` function is called,
with our base ecosystem's name as an argument.

This is also where we have some of our most important constants defined. Most
especially, `SEARCH_QUERIES`. This dictionary is indexed by ecosystem name (the
filename with no extension) that has relevant packages we want to search for.
Define search queries in these ecosystems using filename (or path) and the
keyword to search for.
"""

import logging

from crawler.constants import (
    BASE_ECOSYSTEM,
    CHOOSE_WHAT_TO_DO_MESSAGE,
    DISCLAIMER_MESSAGE,
)
from crawler.counter import count_all_contributors, count_all_repos
from crawler.ecosystem import process_ecosystem

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s\t- %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("stellar-ec-crawler.log"),  # Write logs to this file
        logging.StreamHandler(),  # And also print them to the console
    ],
)


def count_repos():
    """Count all repositories within the entire parent ecosystem."""
    logger.info("Counting repositories")
    count_all_repos(BASE_ECOSYSTEM)


def count_contributors():
    """Count all contributors within the entire parent ecosystem."""
    logger.info("Counting contributors")
    count_all_contributors("PaltaLabs")


def crawl():
    """Start the process by processing the base ecosystem."""
    print(DISCLAIMER_MESSAGE)
    answer = input("Is your locally cloned repo ready? ")

    if answer.lower() == "yes" or answer.lower() == "y":
        logger.info("Crawl function started.")
        process_ecosystem(BASE_ECOSYSTEM)

    elif answer.lower() == "no" or answer.lower() == "n":
        print("That's fine. Run the script again once you're ready.")

    else:
        print("Sorry, I couldn't understand that. Give the script another go please.")


def main():
    """Entry point function."""
    print(CHOOSE_WHAT_TO_DO_MESSAGE)
    answer = input("Enter your chosen number here: ")

    if answer == "1":
        logger.info("Begin crawling Github search")
        crawl()

    elif answer == "2":
        logger.info("Begin counting repositories")
        count_repos()

    elif answer == "3":
        logger.info("Begin counting contributors")
        count_contributors()

    else:
        print("Sorry, I couldn't understand that. Give the script another go please.")


if __name__ == "__main__":
    main()
