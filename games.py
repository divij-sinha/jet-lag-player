import json

import numpy as np

from models import Board, Position


def load_json_game(json_path="rules/connect4s1_rules.json") -> Board:
    with open(json_path, "r") as f:
        game = json.load(f)
        board = Board(**game["rules"])
        return board


class Connect4:
    def __init__(self, json_path: str) -> None:
        self.board = load_json_game(json_path)

    def team_travel(self, team_name: str, new_pos: Position, cost: float) -> None:
        team = self.board.teams[team_name]
        team.current_pos = new_pos
        team.budget -= cost
        print(f"Team {team_name} moved to {new_pos} spending {cost}")

    def pull_card(self, deck_name: str, team_name: str) -> None:
        deck = self.board.decks[deck_name]
        if (team_name == deck.team) or ("any" == deck.team):
            pulled_card_idx = np.random.choice(len(deck.deck))
            pulled_card = deck.deck[pulled_card_idx]
            self.update_deck(deck_name, pulled_card_idx)
            print(f"Team {team_name} pulled card {pulled_card.name}")
            self.board.teams[team_name].current_card = pulled_card
        else:
            print(f"Team {team_name} not allowed to pull from {deck_name}")

    def update_deck(self, deck_name: str, card_idx: int) -> None:
        self.board.decks[deck_name].deck = (
            self.board.decks[deck_name].deck[:card_idx] + self.board.decks[deck_name].deck[card_idx + 1 :]
        )
        print(f"Card no. {card_idx} removed from deck {deck_name}")

    def veto_current_card(self, team_name: str) -> None:
        if self.board.teams[team_name].vetos_used < self.board.teams[team_name].vetos_used:
            self.board.teams[team_name].vetos_used += 1
            self.board.teams[team_name].current_card = None
            print(f"Team {team_name} used veto.")
        else:
            print(f"Team {team_name} cannot use veto.")

    def skip_current_card(self, team_name: str) -> None:
        self.board.teams[team_name].current_card = None
        print(f"Team {team_name} skipped card.")

    def finish_card(self, team_name):
        print(f"Team {team_name} finished card {self.board.teams[team_name].current_card.name}")
        self.board.teams[team_name].budget += self.board.teams[team_name].current_card.victory.budget
        print(f"Team {team_name} budget is now {self.board.teams[team_name].budget}")
        if self.board.teams[team_name].current_card.victory.claim is not None:
            if self.board.teams[team_name].current_card.victory.claim == "current":
                for claim_idx, pos_claim in enumerate(self.board.possible_claims):
                    if (pos_claim.name == self.board.teams[team_name].current_pos.name) and (
                        pos_claim.type == self.board.teams[team_name].current_pos.type
                    ):
                        print(f"Team {team_name} claimed {self.board.teams[team_name].current_pos.name}")
                    if team_name not in self.board.claims.keys():
                        self.board.claims[team_name] = []
                    self.board.claims[team_name].append(pos_claim)
                    self.board.possible_claims = (
                        self.board.possible_claims[:claim_idx] + self.board.possible_claims[claim_idx + 1 :]
                    )
            else:
                print("Don't know how to claim!")


class SchengenShowdown:
    def __init__(self, json_path: str) -> None:
        self.board = load_json_game(json_path)

    def team_travel(self, team_name: str, new_pos: Position, cost: float) -> None:
        messages = []
        team = self.board.teams[team_name]
        team.current_pos = new_pos
        team.budget -= cost
        messages.append(f"Team {team_name} moved to {new_pos.name} spending {cost}")
        for claim_idx, pos_claim in enumerate(self.board.possible_claims):
            if new_pos.name == pos_claim.name:
                for other_teams in self.board.claims.keys():
                    if pos_claim in self.board.claims[other_teams]:
                        messages.append(f"{pos_claim.name} already claimed by {other_teams}")
                        return messages
                messages.append(f"Team {team_name} claimed {pos_claim.name}")
                if team_name not in self.board.claims.keys():
                    self.board.claims[team_name] = []
                self.board.claims[team_name].append(pos_claim)
                self.board.teams[team_name].current_claims.append(pos_claim)

        return messages

    def pull_card(self, deck_name: str, team_name: str) -> None:
        messages = []
        deck = self.board.decks[deck_name]
        if (team_name == deck.team) or ("any" == deck.team):
            for card in deck.deck:
                if card.victory.claim == self.board.teams[team_name].current_pos.name:
                    pulled_card = card
                    messages.append(f"Team {team_name} pulled card {pulled_card.name}")
                    self.board.teams[team_name].current_card = pulled_card
                    return messages

            messages.append("Team not in position to pull card or card already claimed!")
            return messages

    def finish_card(self, team_name):
        print(f"Team {team_name} finished card {self.board.teams[team_name].current_card.name}")
        for card_idx, card in enumerate(self.board.decks[team_name].deck):
            if card.name == self.board.teams[team_name].current_card.name:
                self.board.decks[team_name].deck = (
                    self.board.decks[team_name].deck[:card_idx] + self.board.decks[team_name].deck[card_idx + 1 :]
                )
        for claim_idx, pos_claim in enumerate(self.board.possible_claims):
            if (pos_claim.name == self.board.teams[team_name].current_card.victory.claim) and (
                pos_claim.type == self.board.teams[team_name].current_card.victory.type
            ):
                print(f"Team {team_name} claimed {pos_claim.name}")
            if team_name not in self.board.claims.keys():
                self.board.claims[team_name] = []
            self.board.claims[team_name].append(pos_claim)
            for other_teams in self.board.claims.keys():
                if other_teams != team_name:
                    if pos_claim in self.board.claims[other_teams]:
                        print(f"Team {other_teams} lost claim {pos_claim.name}")
                        self.board.claims[other_teams].remove(pos_claim)
            self.board.possible_claims = self.board.possible_claims[:claim_idx] + self.board.possible_claims[claim_idx + 1 :]
            self.board.teams[team_name].current_claims.append(pos_claim)
