"""
This script collects data about GitHub pull requests
and writes them to PostgreSQL database.
"""

import os
import argparse
from getpass import getpass
from sqlalchemy import create_engine, sql
from github import Github

def parse_args():
    """
    Parses arguments and returns them
    """
    parser = argparse.ArgumentParser(description="Collects statistics related to GitHub pull requests")
    parser.add_argument("org", help="GitHub organization")
    parser.add_argument("--repos", nargs='+', help="list of GitHub repos within the organization",
                        default="all", metavar="REPO")
    parser.add_argument("--db", help="database connection string to which GitHub PR stats will be written",
                        default="postgresql://user:password@localhost/app", dest="db_conn_string")
    return parser.parse_args()

def get_repos(organization, repositories):
    """
    Returns a list of GitHub repos
    :param organization: a GitHub organization
    :param repositories: a list of repositories to get from the organization
    """
    if repositories == "all":
        return organization.get_repos()
    return [organization.get_repo(repo) for repo in repositories]

def process_repo(repository):
    """
    Writes information about a repo to the database
    :param repository: a GitHub repository
    """
    pull_requests = repository.get_pulls(state="closed")
    for pull_request in pull_requests:
        if not pull_request.merged:
            continue
        select_query = sql.text("SELECT id FROM pull_requests WHERE id=:id")
        select_query = select_query.bindparams(id=pull_request.id)
        result = conn.execute(select_query).first()
        if result:
            upsert_query = sql.text("""
                UPDATE pull_requests SET repo = :repo, created_at = :created_at, merged_at = :merged_at, creator = :creator
                WHERE id = :id
            """)
        else:
            upsert_query = sql.text("""
                INSERT INTO pull_requests (id, repo, created_at, merged_at, creator)
                VALUES (:id, :repo, :created_at, :merged_at, :creator)
            """)
        upsert_query = upsert_query.bindparams(id=pull_request.id, repo=repository.name, created_at=pull_request.created_at,
                                               merged_at=pull_request.merged_at, creator=pull_request.user.login)
        conn.execute(upsert_query)

if __name__ == "__main__":
    args = parse_args()
    if os.environ.get("GITHUB_TOKEN") is None:
        token = getpass(prompt="Please enter your GitHub token: ")
    else:
        token = os.environ["GITHUB_TOKEN"]
    gh = Github(token)
    org = gh.get_organization(args.org)
    engine = create_engine(args.db_conn_string, echo=True)
    conn = engine.connect()
    repos = get_repos(org, args.repos)
    for repo in repos:
        process_repo(repo)
