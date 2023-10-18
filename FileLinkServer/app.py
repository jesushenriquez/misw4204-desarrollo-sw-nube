import psycopg2
import datetime
from celery import Celery

app = Celery(
    "auditManager", broker="redis://redis:6379/0", backend="redis://redis:6379/0"
)
app.conf.task_default_queue = "audit_queue"


@app.task
def auditEvent(data):
    employer_username = data.get('employer_username')
    candidate = data.get('candidate')
    data_extraction_date = data.get('data_extraction_date')
    creation_date = datetime.datetime.now()
    print("------------------------")
    print(data)
    print("------------------------")

    with psycopg2.connect(
            dbname="security_db", user="admin", password="password", host="postgres"
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO employer_audit (employer_username, candidate, data_extraction_date, creation_date)
                VALUES (%s, %s, %s, %s);
                """,
                (employer_username, candidate, data_extraction_date, creation_date),
            )
