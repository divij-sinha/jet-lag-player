from typing import Dict, List, Tuple, Optional # Added Optional

from pydantic import BaseModel, Field


class Victory(BaseModel):
    claim: str = Field(default=None)
    budget: float = Field(default=0.0)
    type: str = Field(default=None)


class Card(BaseModel):
    name: str
    challenge: str
    victory: Victory
    effects: Optional[Dict[str, float]] = None # Changed to Optional and default to None
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
    coord: Tuple[float, float] = Field(default=None)
    type: str


# New Model: LocationClaimState
class LocationClaimState(BaseModel):
    name: str  # e.g., country name
    type: str  # e.g., "country"
    challenge_card: Card  # Full Card object embedded here
    status: str  # "unclaimed", "pending", "claimed"
    pending_team_name: Optional[str] = None
    claimed_by_team_name: Optional[str] = None
    teams_at_location: List[str] = Field(default_factory=list)


class Team(BaseModel):
    current_pos: Position
    # current_claims: List[Claim] = Field(default=[]) # Removed
    current_card: Optional[Card] = None # Changed to Optional
    current_challenge_card: Optional[Card] = None # Added
    players: List[str]
    vetos_possible: int = Field(default=0)
    vetos_used: int = Field(default=0)
    budget: float


class Board(BaseModel):
    # claims: Dict[Team, List[Claim]] = Field(default={}) # Removed
    name: str
    teams: Dict[str, Team]
    decks: Dict[str, Deck]
    possible_claims: List[LocationClaimState] # Changed from List[Claim]

    def __str__(self) -> str:
        board_str = f"{self.decks=}"
        return board_str
