# For tables that contain PII and come from an unknown source, how many of them contain an owner tag?

from google.cloud import bigquery
import time

PROJECT_ID = 'etsy-etldata-prod'


def get_missing_metadata_schemas_query() -> str:
    # Query finds the SCHEMAS that have tables where we're missing metadata
    return '''
        SELECT DISTINCT project, dataset
        FROM `etsy-data-warehouse-dev.mmoy.pii_tables_of_unknown_source`
        LEFT JOIN `etsy-data-warehouse-dev.mmoy.pii_tables_of_unknown_source_metadata`
            USING (project, table, dataset)
        WHERE option_value IS NULL
        ORDER BY 1, 2;
    '''


def get_missing_metadata_tables_query(project_id: str, schema: str) -> str:
    # Query finds the TABLES where we're missing metadata
    return f'''
        SELECT DISTINCT project, dataset, table
        FROM `etsy-data-warehouse-dev.mmoy.pii_tables_of_unknown_source`
        LEFT JOIN `etsy-data-warehouse-dev.mmoy.pii_tables_of_unknown_source_metadata`
            USING (project, table, dataset)
        WHERE option_value IS NULL and project = '{project_id}' and dataset = '{schema}'
    '''


def get_metadata_query(project_id: str, schema: str) -> str:
    return f'''
        SELECT project, table, dataset, option_value, 
            REGEXP_EXTRACT(option_value, r'\"owner\"\,\s\"([^(\")]+)\"') as owner, 
            REGEXP_EXTRACT(option_value, r'\"owner_team\"\,\s\"([^(\")]+)\"') as owner_team
        FROM
          ({get_missing_metadata_tables_query(project_id, schema)}) a
        JOIN
          (
            SELECT option_value, table_name as table
            FROM {project_id}.{schema}.INFORMATION_SCHEMA.TABLE_OPTIONS WHERE option_name="labels"
          ) b USING (table)         
    '''


def get_metadata_merge_query(project_id: str, schema: str) -> str:
    return f'''
        MERGE `etsy-data-warehouse-dev.mmoy.pii_tables_of_unknown_source_metadata` main
        USING ({get_metadata_query(project_id, schema)}) staging
        ON main.project = staging.project AND main.dataset = staging.dataset AND main.table = staging.table
        WHEN NOT MATCHED THEN
          INSERT(project, table, dataset, option_value, owner, owner_team)
          VALUES(project, table, dataset, option_value, owner, owner_team)   
    '''


# Do the work
def main():
    client = bigquery.Client(project=PROJECT_ID)

    # find schemas that include tables we're missing metadata for
    rows = client.query(get_missing_metadata_schemas_query()).result()
    schemas = [(row.project, row.dataset) for row in rows]

    for schema_tuple in schemas:
        # for each schema find tables that have PII, check if we have metadata about it and write to BQ if we do
        project_id, schema = schema_tuple

        # check if there is any metadata to save
        rows = client.query(get_metadata_query(project_id, schema)).result()
        if rows.total_rows > 0:
            # save metadata into BQ table
            print(f'Merging data from {project_id}.{schema}')
            client.query(get_metadata_merge_query(project_id, schema))
            time.sleep(5) # don't hammer the server
        else:
            print(f'No metadata for {project_id}.{schema}.  Skipping.')


if __name__ == '__main__':
    main()
