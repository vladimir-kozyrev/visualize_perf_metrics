Purpose
-------
The idea is to visualize individuals' performance metrics using Redash. For that they have to be uploaded to a database.

Currently available metrics
- Confluence documentation updates or new page creation activity within a given space
- GitHub PR count per repo
- GitHub PR average age per repo

Ways to visualize them and justification will be provided in the future.

Run redash with an extra PostgresSQL database
---------------------------------------------

The extra database will be used to store data from various datasources and Redash will take data from it to visualize performance metircs.

[Redash documentation has a guide regarding how to run it locally using docker-compose.](https://redash.io/help/open-source/dev-guide/docker) The following commands work well for the v8.0.0 version of it which gets checked out by default. Redash's docker-compose.yml file needs to be replaced to have the datastore database in the same docker network with Redash.


```shell
$ git submodule update --init --recursive
$ cp docker-compose.yml redash/
$ cd redash/
$ sed -i '/ibm-db/d' requirements_all_ds.txt # this dependency has an issue, so it should be deleted
$ docker-compose up -d
$ npm install
$ docker-compose run --rm server create_db
$ npm run build
$ npm run start
```

Uploading data to the datastore database
----------------------------------------

```shell
$ pip3 install pipenv
$ pipenv install
$ pipenv shell
$ alembic upgrade head
$ python3 github.py -h
$ python3 confluence.py -h
```

Gather data about GitHub pull requests and insert it into the database. You will be asked for the GitHub token. Optionally you can export `GITHUB_TOKEN` environment variable.

```shell
$ python3 github.py mygithuborg --repos repo1 repo2 --db "postgresql://user:password@host/db"
```

Gather data about Confluence documentaion create/update actions in a given space. You will be asked for the password. Optionally you can export `CONFLUENCE_PASSWORD` environment variable.

```shell
$ python3 confluence.py https://myconfluence.atlassian.net XYZ username@domain.com --db "postgresql://user:password@host/db"
```

Now you start visualizing metrics using Redash. [Watch this video to get started](https://www.youtube.com/watch?v=Yn3_QDk2qQM).

Next steps
----------

- add a script to copy data from Jira to the datastore
- add SQL queries for each of the metrics
- describe how these metrics can reflect on performance
