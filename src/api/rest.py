from fastapi import FastAPI
from schemas import GameList, StatusMessage, PlatformRequest
from db.handler import MyDb

db = MyDb()
app = FastAPI()

@app.post('/post/games', response_model = StatusMessage)
def post_games(game_list: GameList):
    pass

@app.get('/get/all', response_model = GameList)
def get_games():
    pass

@app.get('/get/platform', response_model = GameList)
def get_games_platform(request: PlatformRequest):
    pass