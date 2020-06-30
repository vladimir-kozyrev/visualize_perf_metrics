from github import Github
from sqlalchemy import create_engine, sql
from getpass import getpass
import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Collects statistics related to GitHub pull requests")
    parser.add_argument("org", help="GitHub organization")
    parser.add_argument("team", help="GitHub team within the organzation")
    parser.add_argument("--repos", nargs='+', help="list of GitHub repos within the organization",
        default="all", metavar="REPO"),
    parser.add_argument("--db", help="database connection string to which GitHub PR stats will be written",
        default="postgresql://user:password@localhost/app", dest="db_conn_string")
    return parser.parse_args()

def find_team_with_name(teams, name):
    for team in teams:
        if team.name == name:
            return team
    raise Exception(f"Team with name {name} has not been found.")

def get_team_repos(team, repos):
    if repos == "all":
        return [repo for repo in team.get_repos()]
    return [repo for repo in team.get_repos() if repo.name in args.repos]

def process_repo(repo):
    pull_requests = repo.get_pulls(state="closed")
    for pr in pull_requests:
        if pr.merged != True:
            continue
        query = sql.text("INSERT INTO pull_requests (id, created_at, merged_at, login) VALUES (:id, :created_at, :merged_at, :login)",)
        query = query.bindparams(id=pr.id, created_at=pr.created_at, merged_at=pr.merged_at, login=pr.user.login)
        conn.execute(query)

if __name__ == "__main__":
    args = parse_args()
    if os.environ.get("GITHUB_TOKEN") is None:
        token = getpass(prompt="Please enter your GitHub token: ")
    else:
        token = os.environ["GITHUB_TOKEN"]
    gh = Github(token)
    org_teams = gh.get_organization(args.org).get_teams()
    target_team = find_team_with_name(org_teams, args.team)
    team_repos = get_team_repos(target_team, args.repos)
    engine = create_engine(args.db_conn_string, echo=True)
    conn = engine.connect()
    for repo in team_repos:
        process_repo(repo)
