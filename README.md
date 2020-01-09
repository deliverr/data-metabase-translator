# metabase-translator
Translate metabase queries from one SQL dialect to another. 

When Deliverr migrated from Redshift to Snowflake, we automated conversion of our 1,500+ [Metabase](https://www.metabase.com/) 
reporting queries. For anyone who needs to go through a similar migration, this python script may be useful.
 
For those not using Metabase but in need of SQL translation, it may be worthwhile to extract the `SqlTranslator`
class for that purpose. 

## Installation

A Pipfile is included, so that after cloning the repo `pipenv install` will install needed dependencies.

## Configuration

Rename `metabase.sample.yaml` to `metabase.yaml` and update:
  - Metabase database connection properties
  - Source and target database ids from the `metabase_database` Postgresql table.
  
Run the `ddl/create_report_card_migration.ddl` in your Metabase Postgresql instance to create a migration table.
  
## Usage

Within a pipenv shell, run `python translate.py`. When all goes well, it will output lines like the following:

```bash
Retrieved 1500 native queries 
Wrote 1500 rows to report_card_migration
```

Apply the migration changes with:

```postgresql
UPDATE report_card
SET dataset_query = migration.dataset_query,
    database_id = migration.target_database_id
FROM report_card_migration AS migration
WHERE report_card.id = migration.card_id;
```

## Development

SQL dialect rules for Redshift to Snowflake conversion are in [translator/redshift_to_snowflake.py](translator/redshift_to_snowflake.py).
Beyond that, we hope that the code is straight-forward to read and modify.

Pull requests are welcome.

## References

  - Fishtown Analytic's blog post [How Compatible are Redshift and Snowflake's SQL Syntaxes?](https://medium.com/@jthandy/how-compatible-are-redshift-and-snowflakes-sql-syntaxes-c2103a43ae84)
  - [python-sqlparse](https://sqlparse.readthedocs.io/en/latest/)

## License

This project is licensed under the terms of the GNU General Public License v3.0.