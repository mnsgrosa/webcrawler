from fastapi import FastAPI
from schemas import GameList, StatusMessage, PlatformRequest
from db.handler import MyDb

db = MyDb()
app = FastAPI()

@app.post('/post/games', response_model = StatusMessage)
def post_games(game_list: GameList):
    columns =  game_list.items[0].model_fields
    db.upsert_data(game_list.items, columns.items)
    return {'status': True}

@app.get('/get/all')
def get_games():
    data = db.get_all_data()
    return {'data': data}


@app.get('/get/platform', response_model = GameList)
def get_games_platform(request: PlatformRequest):
    data = db.get_specific_games(request.platform, request.date)
    return {'items': data}