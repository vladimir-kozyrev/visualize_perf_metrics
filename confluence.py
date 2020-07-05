from atlassian import Confluence
from sqlalchemy import create_engine, sql
from getpass import getpass
import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Determines how many Confluence pages were created and edited by each user in a space")
    parser.add_argument("url", help="Confluence URL")
    parser.add_argument("space", help="Confluence space")
    parser.add_argument("username", help="Confluence username")
    parser.add_argument("--db", help="database connection string to which the stats will be written",
        default="postgresql://user:password@localhost/app", dest="db_conn_string")
    return parser.parse_args()

def update_contributors(created_by, contributors):
    if contributors.get(created_by) is None:
        contributors[created_by] = 1
    else:
        contributors[created_by] += 1

def process_page(page, contributors):
    page_title = page["title"]
    page_id = page["id"]
    page_version = page["version"]["number"]
    print(f"Processing '{page_title}' page. It's current version is {page_version}.")
    for version in range(page_version, 0, -1):
        if version == page_version:
            update_contributors(page["version"]["by"]["displayName"], contributors)
            continue
        # collect info about previous versions of the page if there are any
        prev_page_version = confluence.get_page_by_id(page_id, expand="version", version=version)
        update_contributors(prev_page_version["version"]["by"]["displayName"], contributors)

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
        query = sql.text("""
            INSERT INTO confluence (person, contributions)
            VALUES (:person, :contributions)
        """)
        query = query.bindparams(person=person, contributions=contributions)
        conn.execute(query)
