from fastapi import FastAPI
import uvicorn
from src.api.schemas import GameList, StatusMessage, PlatformRequest
from src.api.db.handler import MyDb

db = MyDb()
app = FastAPI()

@app.post('/post/games')
def post_games(game_list: GameList):
    upsert = [game.model_dump() for game in game_list.items]
    db.upsert_data(upsert)
    return {'status': upsert}

@app.get('/get/all')
def get_games():
    data = db.get_all_data()
    return {'data': data}

@app.get('/get/platform')
def get_games_platform(platform: str, date: str = None):
    df = db.get_specific_games(platform, date)
    list_of_games = df.to_dict(orient='records')
    return {'items': list_of_games}