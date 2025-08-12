import psycopg2
import pandas as pd
from typing import List, Any
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
        returnable_data = pd.DataFrame(data, columns = data[0].description)
        return data

    def get_specific_games(self, platform: str = 'playstation', date: str = None):
        if platform is None:
            return pd.DataFrame()
        
        query = '''
            SELECT * FROM deals_schema.deals
            '''

        query += f'WHERE platform = {platform}'
            
        if date:
            query += f'AND date = {date}'
            

        with self.get_cursor() as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
        columns = data[0].description
        returnable_data = pd.DataFrame(data, columns = columns)
        return returnable_data

    def upsert_data(self, data:List[Any], columns:List[str]):
        if value is None or columns is None:
            return False

        try:
            query = f'''
            INSERT INTO deals_schema.deals
                date,
                platform,
                game_name,
                game_type,
                price
            VALUES (%s, %s, %s, %s, %s)
            '''
            
            with self.get_cursor() as cursor:
                cursor.executemany(query, data)
            return True
        except Exception as e:
            return False