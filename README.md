Purpose
-------
The idea is to visualize individuals' performance metrics using Redash. For that they have to be uploaded to a database.

Uploading data to the database
------------------------------

```shell
$ pip3 install pipenv
$ pipenv install
$ pipenv shell
$ python3 github_prs_to_database.py yourgithuborg --repos repo1 repo2 --db "postgresql://user:password@host/db"
```

Next steps
----

- describe how to run redash using docker compose alongside postgres
- add more data to the database
- describe metrics that can be visualized
