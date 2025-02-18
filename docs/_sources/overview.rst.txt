Overview of the Check Application
#################################

General Information
-------------------

Check Application is a back-end service that allows users to create and share financial checks via a REST API.

Author
------
`Yaroslav Khoruzhenko <https://github.com/yakhoruzhenko>`_

Stack
------

This application is built using the following technologies:

- **FastAPI**: https://fastapi.tiangolo.com
- **Uvicorn**: https://www.uvicorn.org
- **SQLAlchemy**: https://www.sqlalchemy.org
- **PostgreSQL**: https://www.postgresql.org

Configuration
-------------
The Check Application relies on environment variables for its configuration. These variables should be provided in the application's environment, typically through the docker-compose file. If not explicitly set, the application will fallback to default values.

The application relies on the following environment variables (values may vary):

.. code-block:: ini

    APP_VERSION="0.1.2"
    ENVIRONMENT="dev"
    ADMIN_TOKEN="test1234"
    CHECK_LINE_LENGTH: 40  # Maximum number of characters per line in the text representation of a check
    SECRET_KEY="fcb83a311c0ab22310e16417b84de96d496c5f80906b4e14c00b15de44f56a8c"
    ACCESS_TOKEN_EXPIRE_MINUTES=1440 # 24 hours
    HASHING_ALGORITHM="HS256"
    PGHOST="postgres"
    PGPORT=5432
    PGDATABASE="check_app"
    PGUSER="check"
    PGPASSWORD="password"

Ensure these variables are properly set in your environment to configure the application correctly.

 .. note::
    
    When the ENVIRONMENT value is set to anything other than dev, the admin panel route and OpenAPI documentation will be disabled.

Updating the docs
-----------------
The docs are built using Sphinx.
Install the Sphinx requirements into your virtual environment before building with:

.. code-block:: bash

    pip3 install -r docs/requirements.txt

To build the documentation locally, add or adjust the corresponding sections, then run:

.. code-block:: bash

    make docs
