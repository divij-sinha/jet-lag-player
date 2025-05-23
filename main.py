from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from games import SchengenShowdown
from models import Position

# connect4_s1 = Connect4("rules/connect4s1_rules.json")
# print(connect4_s1.board)
# print("----")
templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
schengen_showdown_s13 = SchengenShowdown("rules/schengenshowdowns13.json")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "board": schengen_showdown_s13.board, "title": "Schengen Showdown S13"})


@app.get("/team_travel")
def team_travel(request: Request, team_name: str, new_pos: str, cost: int = 0):
    new_pos = Position(name=new_pos, type="country")
    messages = schengen_showdown_s13.team_travel(team_name, new_pos, cost)
    return templates.TemplateResponse("index.html", {"request": request, "board": schengen_showdown_s13.board, "messages": messages, "title": "Schengen Showdown S13"})


@app.get("/pull_card")
def pull_card(request: Request, team_name: str):
    messages = schengen_showdown_s13.pull_card("main_deck", team_name)
    return templates.TemplateResponse("index.html", {"request": request, "board": schengen_showdown_s13.board, "messages": messages, "title": "Schengen Showdown S13"})
