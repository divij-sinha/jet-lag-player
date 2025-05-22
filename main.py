from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from games import SchengenShowdown
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
def team_travel(request: Request, team_name: str, new_pos: str, cost: int = 0):
    new_pos = Position(name=new_pos, type="country")
    messages = schengen_showdown_s13.team_travel(team_name, new_pos, cost)
    return templates.TemplateResponse("index.html", {"request": request, "board": schengen_showdown_s13.board, "messages": messages})


@app.get("/pull_card")
def pull_card(request: Request, team_name: str):
    messages = schengen_showdown_s13.pull_card("main_deck", team_name)
    return templates.TemplateResponse("index.html", {"request": request, "board": schengen_showdown_s13.board, "messages": messages})


@app.get("/finish_card")
async def finish_card(request: Request, team_name: str):
    messages = schengen_showdown_s13.finish_card(team_name)
    return templates.TemplateResponse("index.html", {"request": request, "board": schengen_showdown_s13.board, "messages": messages})
