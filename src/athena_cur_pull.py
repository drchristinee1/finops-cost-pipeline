import time
import boto3
import pandas as pd


AWS_REGION = "us-east-1"
ATHENA_DATABASE = "your_cur_database"
S3_OUTPUT = "s3://your-athena-query-results-bucket/folder/"

QUERY = """
SELECT
    line_item_usage_start_date AS Date,
    product_product_name AS Service,
    line_item_usage_amount AS Usage,
    line_item_unblended_cost AS Cost,
    resource_tags_user_team AS Team,
    resource_tags_user_workload AS Workload
FROM your_cur_table
WHERE line_item_usage_start_date >= date '2026-05-01'
LIMIT 100
"""


def run_athena_query(query: str) -> pd.DataFrame:
    athena = boto3.client("athena", region_name=AWS_REGION)

    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={"Database": ATHENA_DATABASE},
        ResultConfiguration={"OutputLocation": S3_OUTPUT},
    )

    query_execution_id = response["QueryExecutionId"]

    while True:
        status_response = athena.get_query_execution(
            QueryExecutionId=query_execution_id
        )

        status = status_response["QueryExecution"]["Status"]["State"]

        if status in ["SUCCEEDED", "FAILED", "CANCELLED"]:
            break

        time.sleep(2)

    if status != "SUCCEEDED":
        raise RuntimeError(f"Athena query failed with status: {status}")

    results = athena.get_query_results(QueryExecutionId=query_execution_id)

    columns = [
        col["Label"]
        for col in results["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]
    ]

    rows = []
    for row in results["ResultSet"]["Rows"][1:]:
        rows.append([
            item.get("VarCharValue", None)
            for item in row["Data"]
        ])

    return pd.DataFrame(rows, columns=columns)


if __name__ == "__main__":
    df = run_athena_query(QUERY)

    print("CUR data pulled from Athena:")
    print(df.head())

    df.to_csv("data/raw_cost_from_athena.csv", index=False)