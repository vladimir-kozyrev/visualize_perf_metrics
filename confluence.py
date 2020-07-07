"""
This script collects data about Confluence page create and edit activities
and writes them to PostgreSQL database.
"""

import os
import argparse
from getpass import getpass
from atlassian import Confluence
from sqlalchemy import create_engine, sql

def parse_args():
    """
    Parses arguments and return them
    """
    parser = argparse.ArgumentParser(description="Determines how many Confluence pages were created and edited by each user in a space")
    parser.add_argument("url", help="Confluence URL")
    parser.add_argument("space", help="Confluence space")
    parser.add_argument("username", help="Confluence username")
    parser.add_argument("--db", help="database connection string to which the stats will be written",
                        default="postgresql://user:password@localhost/app", dest="db_conn_string")
    return parser.parse_args()

def increment_dict_value(a_dict, key):
    """
    Increments the value related to a given key by 1
    :param key: a dictionary key
    :param a_dict: a dictionary
    """
    if a_dict.get(key) is None:
        a_dict[key] = 1
    else:
        a_dict[key] += 1

def process_page(confluence_page, confluence_users):
    """
    Processes page by making a request to the Confluence API
    :param confluence_page: a Confluence page
    :param contributors: a dictionary of people who contributed to a Confluence space
    """
    page_title = confluence_page["title"]
    page_id = confluence_page["id"]
    page_version = confluence_page["version"]["number"]
    print(f"Processing '{page_title}' page. It's current version is {page_version}.")
    for version in range(page_version, 0, -1):
        if version == page_version:
            confluence_user = confluence_page["version"]["by"]["displayName"]
            increment_dict_value(confluence_users, confluence_user)
            continue
        # collect info about previous versions of the page if there are any
        prev_page_version = confluence.get_page_by_id(page_id, expand="version", version=version)
        confluence_user = prev_page_version["version"]["by"]["displayName"]
        increment_dict_value(confluence_users, confluence_user)

if __name__ == "__main__":
    args = parse_args()
    if os.environ.get("CONFLUENCE_PASSWORD") is None:
        password = getpass(prompt="Please enter your Confluence password: ")
    else:
        password = os.environ["CONFLUENCE_PASSWORD"]
    confluence = Confluence(
        url=args.url,
        username=args.username,
        password=password
    )
    contributors = {}
    pages = confluence.get_all_pages_from_space(args.space, expand="version", limit=999)
    for page in pages:
        process_page(page, contributors)
    engine = create_engine(args.db_conn_string, echo=True)
    conn = engine.connect()
    for person, contributions in contributors.items():
        select_query = sql.text("SELECT person, contributions FROM confluence WHERE person=:person")
        select_query = select_query.bindparams(person=person)
        result = conn.execute(select_query).first()
        if result:
            upsert_query = sql.text("""
                UPDATE confluence SET contributions = :contributions
                WHERE person = :person
            """)
        else:
            upsert_query = sql.text("""
                INSERT INTO confluence (person, contributions)
                VALUES (:person, :contributions)
            """)
        upsert_query = upsert_query.bindparams(person=person, contributions=contributions)
        conn.execute(upsert_query)
