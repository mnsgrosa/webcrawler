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

@app.get('/get/platform', response_model = GameList)
def get_games_platform(request: PlatformRequest):
    data = db.get_specific_games(request.platform, request.date)
    return {'items': data}

if __name__ == '__main__':
    uvicorn.run(app, host = '0.0.0.0', port = 8000)