from typing import Any

from sqlalchemy import text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Query, Session


def explain_analyze(session: Session, query: Query[Any]) -> None:
    # Compile the query to get the SQL string
    compiled_query = query.statement.compile(dialect=postgresql.dialect(), compile_kwargs={'literal_binds': True})
    
    explain_query = text(f'EXPLAIN ANALYZE {compiled_query}')
    
    result = session.execute(explain_query)

    # Print the execution plan
    print('\n'.join(row[0] for row in result))
