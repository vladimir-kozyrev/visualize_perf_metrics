from atlassian import Confluence

import pprint
pp = pprint.PrettyPrinter(indent=4)

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
        print(f"Processing {page['title']} page")
        page_id = page["id"]
        page_version = page["version"]["number"]
        # iterate over previous versions of the page
        for version in range(page_version, 0, -1):
            if page_version == 1:
                update_contributors(page["version"]["by"]["displayName"], contributors)
                continue
            page_ver = confluence.get_page_by_id(page_id, expand="version", version=version)
            update_contributors(page_ver["version"]["by"]["displayName"], contributors)
    pp.pprint(contributors)
