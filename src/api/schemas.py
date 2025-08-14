from pydantic import BaseModel, Field
from typing import List, Optional, Any

class StatusMessage(BaseModel):
    status:bool = Field(default = True, description = 'Request done or not')
    error:Optional[str] = ''

class GameData(BaseModel):
    date:str =  Field(..., description = 'Date of deal scraping')
    platform:str = Field(..., description = 'Which website was scraped')
    game_name:str = Field(..., description = 'Game name')
    game_type:str = Field(..., description = 'Game type')
    price:float = Field(..., description = 'Price of the game')

class GameList(BaseModel):
    items: List[GameData]