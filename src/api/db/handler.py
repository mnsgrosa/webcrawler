import psycopg2
from contextlib import contextmanager

class MyDb:
    def __init__(self):
        self.connection = psycopg2.connec(
            dbname = 'deals_db',
            user = 'psql',
            password = 'my_password',
            host = 'localhost',
            port = 5432
        )

    @contextmanger
    def get_cursor():
        cursor = None
        try:
            cursor = self.connection.cursor()
            yield cursor
            cursor.commit()
        except Exception as e:
            if self.connection:
                self.connection.close()
            raise e
        finally:
            if cursor:
                cursor.close()
    
    def get_all_data(self):
        with self.get_cursor() as cursor:
            cursor.execute('''
            SELECT * FROM deals_schema.deals
            ''')
            data = cursor.fetchall()
        return data

    def get_specific_games(self, platform: str = 'playstation', date: str = None):
        if platform is None:
            return {}

        with self.get_cursor() as cursor:
            query = '''
            SELECT * FROM deals_schema.deals
            '''

            query += f'WHERE platform = {platform}'
            
            if date:
                query += f'AND date = {date}'
            
            cursor.execute(query)
            data = cursor.fetchall()
        return data