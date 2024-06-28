"""## Crawler

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

from dotenv import load_dotenv

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s\t-%(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("stellar-ec-crawler.log"),  # Write logs to this file
        logging.StreamHandler(),  # And also print them to the console
    ],
)

# Constants and configurations
BASE_ECOSYSTEM: str = "Stellar"
DISCLAIMER_MESSAGE: str = """Welcome to the Stellar EC Scraper!

This script will modify the relevant ecosystem TOML file(s) **in place**. So,
it's really important that you have done three (3) things:

1. You have specified in the `.env` file, the absolute path to your local clone
   of the EC repo, and
2. Your local clone's `master` branch is up-to-date with the upstream EC repo,
   and
3. You should also check out a new branch your changes can be applied to. (This
   script won't apply any changes to your repo, but it could make it easier on
   you later if you're already on a new branch.)

If you haven't done those three (3) things, you could possibly screw up your
local clone. So, you might just double-check...

Please confirm below with '[y]es' or '[n]o'
"""


def main():
    """Start the process by processing the base ecosystem."""
    print(DISCLAIMER_MESSAGE)
    answer = input("Is your locally cloned repo ready? ")

    if answer.lower() == "yes" or answer.lower() == "y":
        # pylint: disable=import-outside-toplevel
        from crawler.ecosystem import process_ecosystem

        logger.info("Main function started.")
        process_ecosystem(BASE_ECOSYSTEM)

    elif answer.lower() == "no" or answer.lower() == "n":
        print("That's fine. Run the script again once you're ready.")

    else:
        print("Sorry, I couldn't understand that. Give the script another go please.")


if __name__ == "__main__":
    main()
