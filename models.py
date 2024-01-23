from pydantic import BaseModel, Field
from decimal import Decimal
from typing import List, Tuple, Dict, Optional


class Victory(BaseModel):
    claim: str = Field(default=None)
    budget: float = Field(default=0.0)


class Card(BaseModel):
    name: str
    challenge: str
    victory: Victory
    effects: Dict[str, float] = Field(default=None)
    card_budget: float = Field(default=0.0)

    def __repr__(self) -> str:
        card_repr = f"{self.name}\n{self.challenge}\n"
        return card_repr


class Deck(BaseModel):
    deck: List[Card]
    team: str

    def __repr__(self) -> str:
        deck_repr = f"TEAM - {self.team}\n\n" + self.deck.__repr__()
        return deck_repr


class Claim(BaseModel):
    name: str
    type: str


class Position(BaseModel):
    name: str
    coord: Tuple[float, float]
    type: str


class Team(BaseModel):
    current_pos: Position
    current_claims: List[Claim] = Field(default=[])
    current_card: Card = Field(default=None)
    players: List[str]
    vetos_possible: int
    vetos_used: int = Field(default=0)
    budget: float


class Board(BaseModel):
    claims: Dict[Team, List[Claim]] = Field(default={})
    name: str
    teams: Dict[str, Team]
    decks: Dict[str, Deck]
    possible_claims: List[Claim]

    def __str__(self) -> str:
        board_str = f"{self.decks=}"
        return board_str
