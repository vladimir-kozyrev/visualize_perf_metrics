from github import Github
from sqlalchemy import create_engine, sql
from getpass import getpass
import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Collects statistics related to GitHub pull requests")
    parser.add_argument("org", help="GitHub organization")
    parser.add_argument("--repos", nargs='+', help="list of GitHub repos within the organization",
        default="all", metavar="REPO"),
    parser.add_argument("--db", help="database connection string to which GitHub PR stats will be written",
        default="postgresql://user:password@localhost/app", dest="db_conn_string")
    return parser.parse_args()

def get_repos(org, repos):
    if repos == "all":
        return org.get_repos()
    return [org.get_repo(repo) for repo in repos]

def process_repo(repo):
    pull_requests = repo.get_pulls(state="closed")
    for pr in pull_requests:
        if pr.merged != True:
            continue
        query = sql.text("""
            INSERT INTO pull_requests (id, repo, created_at, merged_at, creator)
            VALUES (:id, :repo, :created_at, :merged_at, :creator)
        """,)
        query = query.bindparams(id=pr.id, repo=repo.name, created_at=pr.created_at,
            merged_at=pr.merged_at, creator=pr.user.login, )
        conn.execute(query)

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
