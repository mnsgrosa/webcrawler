import psycopg2
import pandas as pd
from typing import List, Any
from contextlib import contextmanager
from src.utils.logger import MyLogger

class MyDb(MyLogger):
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
            self.logger.info('Creating cursor')
            cursor = self.connection.cursor()
            yield cursor
            self.logger.info('Commiting changes')
            cursor.commit()
        except Exception as e:
            self.logger.error(f'Couldnt create cursor: {e}')
            if self.connection:
                self.connection.close()
            raise e
        finally:
            self.logger.info('Closing cursor')
            if cursor:
                cursor.close()
    
    def get_all_data(self):
        try:
            self.logger.info('Getting all data from database')
            with self.get_cursor() as cursor:
                cursor.execute('''
                SELECT * FROM deals_schema.deals
                ''')
                data = cursor.fetchall()
            self.logger.info('Data retrieved from db')
            returnable_data = pd.DataFrame(data, columns = data[0].description)
            return data
        except Exception as e:
            self.logger.error(f'Couldnt get data: {e}')
            return pd.DataFrame()

    def get_specific_games(self, platform: str = 'playstation', date: str = None):
        if platform is None:
            self.logger.info('No platform provided')
            return pd.DataFrame()
        
        try:
            self.logger.info(f'Getting {platform}')
            query = '''
                SELECT * FROM deals_schema.deals
                '''

            query += f'WHERE platform = {platform}'
                
            if date:
                self.logger.info(f'and {date}')
                query += f'AND date = {date}'
                

            self.logger.info('Executing query')
            with self.get_cursor() as cursor:
                cursor.execute(query)
                data = cursor.fetchall()
            self.logger.info(f'Got data from {platform}')
            columns = data[0].description
            returnable_data = pd.DataFrame(data, columns = columns)
            return returnable_data
        except Exception as e:
            self.logger.error(f'Couldnt get data: {e}')
            return pd.DataFrame()

    def upsert_data(self, data:List[Any]):
        if data is None:
            self.logger.info(f'Invalid format: {data}')
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
            
            self.logger.info('Starting to upsert data')
            with self.get_cursor() as cursor:
                cursor.executemany(query, data)
            self.logger.info('Data upserted')
            return True
        except Exception as e:
            self.logger.error(f'Couldnt upsert data: {e}')
            return False