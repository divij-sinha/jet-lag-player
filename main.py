from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from typing import Optional # Added Optional

from games import SchengenShowdown
# Position might not be needed if team_travel directly takes new_pos_name as str
from models import Position 

# connect4_s1 = Connect4("rules/connect4s1_rules.json")
# print(connect4_s1.board)
# print("----")
templates = Jinja2Templates(directory="templates")

app = FastAPI()

schengen_showdown_s13 = SchengenShowdown("rules/schengenshowdowns13.json")
print(schengen_showdown_s13.board)
print("----")


@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "board": schengen_showdown_s13.board})


@app.get("/team_travel")
def team_travel(request: Request, team_name: str, new_pos_name: str, cost: int = 0):
    # The game logic for team_travel now expects new_pos_name as a string
    # Position object creation is handled within the game logic if needed, or team.current_pos is directly a string.
    # Based on previous refactoring, team.current_pos is a Position object, 
    # but team_travel in games.py expects new_pos_name as str.
    messages = schengen_showdown_s13.team_travel(team_name=team_name, new_pos_name=new_pos_name, cost=cost)
    return templates.TemplateResponse("index.html", {"request": request, "board": schengen_showdown_s13.board, "messages": messages})


# Removed /pull_card endpoint


@app.get("/complete_challenge")
async def complete_challenge_endpoint(request: Request, team_name: str):
    messages = schengen_showdown_s13.complete_challenge(team_name)
    return templates.TemplateResponse("index.html", {"request": request, "board": schengen_showdown_s13.board, "messages": messages})

@app.get("/attempt_challenge")
async def attempt_challenge_endpoint(request: Request, team_name: str, location_name: Optional[str] = None):
    messages = schengen_showdown_s13.attempt_challenge(team_name=team_name, location_name=location_name)
    return templates.TemplateResponse("index.html", {"request": request, "board": schengen_showdown_s13.board, "messages": messages})
