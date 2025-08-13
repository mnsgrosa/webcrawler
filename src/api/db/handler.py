import psycopg2
import pandas as pd
from typing import List, Dict, Any
from contextlib import contextmanager
from src.utils.logger import MyLogger

class MyDb(MyLogger):
    def __init__(self):
        super().__init__(__name__)
        self.connection = psycopg2.connect(
            dbname = 'deals_db',
            user = 'postgres',
            password = 'my_password',
            host = 'db',
            port = 5432
        )

    @contextmanager
    def get_cursor(self):
        cursor = None
        try:
            self.logger.info('Creating cursor')
            cursor = self.connection.cursor()
            yield cursor
            self.logger.info('Commiting changes')
            self.connection.commit()
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
                columns = [desc[0] for desc in cursor.description]
            self.logger.info('Data retrieved from db')
            returnable_data = pd.DataFrame(data, columns = columns)
            return data
        except Exception as e:
            self.logger.error(f'Couldnt get data: {e}')
            return pd.DataFrame()

    def get_specific_games(self, platform: str = 'playstation', date: str = None):
        if platform is None:
            self.logger.info('No platform provided')
            return pd.DataFrame()
        
        try:
            self.logger.info(f'Getting games for platform: {platform}')
            query = 'SELECT * FROM deals_schema.deals WHERE platform = %s'
            params = [platform]

            if date:
                self.logger.info(f'and date: {date}')
                query += ' AND date = %s'
                params.append(date)

            self.logger.info('Executing query')
            with self.get_cursor() as cursor:
                cursor.execute(query, tuple(params))
                data = cursor.fetchall()

            if not data:
                self.logger.info(f'No data found for the specified criteria.')
                return pd.DataFrame()

            self.logger.info(f'Got data from {platform}')
            columns = [desc[0] for desc in cursor.description]
            returnable_data = pd.DataFrame(data, columns=columns)
            return returnable_data

        except Exception as e:
            self.logger.error(f'Couldnt get data: {e}')
            return pd.DataFrame()
    
    def upsert_data(self, data:List[Dict[str, Any]]):
        if data is None:
            self.logger.info(f'Invalid format: {data}')
            return False

        try:
            query = f'''
            INSERT INTO deals_schema.deals(
                date,
                platform,
                game_name,
                game_type,
                price
            )
            VALUES (%s, %s, %s, %s, %s)
            '''
            
            values_to_insert = [
                (
                item['date'],
                item['platform'],
                item['game_name'],
                item['game_type'],
                item['price']
                ) for item in data
            ]

            self.logger.info('Starting to upsert data')
            with self.get_cursor() as cursor:
                cursor.executemany(query, values_to_insert)
            self.logger.info('Data upserted')
            return True
        except Exception as e:
            self.logger.error(f'Couldnt upsert data: {e}')
            return False