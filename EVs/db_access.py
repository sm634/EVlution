import pandas as pd
from sqlalchemy import create_engine


class DBAccess:

    """initialise the database access details needed to establish a connection."""
    def __init__(
            self,
            db_type='mysql',
            db_user='admin1',
            db_pass='SMreJiPr!th1',
            db_host='database-evlution.czp2g8kfgpt8.eu-west-2.rds.amazonaws.com',
            db_port='3306',
            driver='mysql+pymysql',
            database='evlution_db'
            ):

        self.db_type = db_type
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_host = db_host
        self.db_port = db_port
        self.driver = driver
        self.database = database

        if self.db_type.lower() == 'mysql':
            self.engine = create_engine(
                f"{self.driver}://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.database}"
            )

    def write_to_db(self,
                    df: pd.DataFrame,
                    table_name: str
                    ):
        """
        A method that can be used to write to the database.
        """

        connection = self.engine.connect()
        df.to_sql(con=connection, name=table_name, chunksize=1000, if_exists='replace')
        connection.close()
