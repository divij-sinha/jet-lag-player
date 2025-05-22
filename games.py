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

    def team_travel(self, team_name: str, new_pos: Position, cost: float) -> list[str]:
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

    def pull_card(self, deck_name: str, team_name: str) -> list[str]:
        messages = []
        
        if deck_name not in self.board.decks:
            messages.append(f"Deck '{deck_name}' not found.")
            return messages
        source_deck_model = self.board.decks[deck_name]

        team = self.board.teams[team_name]

        if not ((team_name == source_deck_model.team) or ("any" == source_deck_model.team)):
            messages.append(f"Team {team_name} is not allowed to pull from deck {deck_name}.")
            return messages

        if not team.current_pos:
            messages.append(f"Team {team_name} has no current position, cannot determine card eligibility.")
            return messages
            
        if team.current_card:
            messages.append(f"Team {team_name} already has an active card: {team.current_card.name}. Finish it first.")
            return messages

        card_to_pull_idx = -1
        pulled_card_obj = None # Use a different variable name to avoid confusion

        for idx, card_in_deck in enumerate(source_deck_model.deck):
            if card_in_deck.victory.claim == team.current_pos.name:
                # Check if this claim is still available in board.possible_claims
                is_claim_still_available = any(
                    pc.name == card_in_deck.victory.claim and pc.type == card_in_deck.victory.type
                    for pc in self.board.possible_claims
                )
                
                if is_claim_still_available:
                    pulled_card_obj = card_in_deck
                    card_to_pull_idx = idx
                    break # Found a suitable card
                # else:
                    # Optionally, message if card targets an already claimed location
                    # messages.append(f"Card '{card_in_deck.name}' targets location '{card_in_deck.victory.claim}', which is no longer available.")
        
        if pulled_card_obj is not None and card_to_pull_idx != -1:
            team.current_card = pulled_card_obj
            source_deck_model.deck.pop(card_to_pull_idx) # Remove the card from the source deck
            messages.append(f"Team {team_name} pulled card '{pulled_card_obj.name}' from {deck_name}. Card removed from source deck.")
        else:
            messages.append(f"Team {team_name} could not pull a card from {deck_name} for their current location '{team.current_pos.name}'. This could be because no card targets this location, the location is already claimed, or the deck is empty.")
        
        return messages

    def finish_card(self, team_name: str) -> list[str]:
        messages = []
        current_card = self.board.teams[team_name].current_card
        if not current_card:
            messages.append(f"Team {team_name} has no current card to finish.")
            return messages

        messages.append(f"Team {team_name} completed card '{current_card.name}'.")

        # Card is considered consumed from the main deck when pulled.
        # No need to remove it from a team-specific deck here.

        # Process victory rewards (e.g., budget)
        if current_card.victory.budget > 0:
            self.board.teams[team_name].budget += current_card.victory.budget
            messages.append(f"Team {team_name} budget increased by {current_card.victory.budget} to {self.board.teams[team_name].budget}.")

        # Process claims
        if current_card.victory.claim:
            claim_name_to_acquire = current_card.victory.claim
            claim_type_to_acquire = current_card.victory.type
            
            target_claim_found = False
            for claim_idx, pos_claim in enumerate(self.board.possible_claims):
                if pos_claim.name == claim_name_to_acquire and pos_claim.type == claim_type_to_acquire:
                    target_claim_found = True
                    messages.append(f"Team {team_name} attempting to claim {pos_claim.name} ({pos_claim.type}).")

                    # Add to team's claims
                    if team_name not in self.board.claims:
                        self.board.claims[team_name] = []
                    self.board.claims[team_name].append(pos_claim)
                    self.board.teams[team_name].current_claims.append(pos_claim)
                    messages.append(f"Team {team_name} successfully claimed {pos_claim.name} ({pos_claim.type}).")

                    # Remove claim from other teams if they have it
                    for other_team_name, other_team_claims in self.board.claims.items():
                        if other_team_name != team_name:
                            if pos_claim in other_team_claims:
                                self.board.claims[other_team_name].remove(pos_claim)
                                # Also remove from their current_claims if it's tracked there
                                if pos_claim in self.board.teams[other_team_name].current_claims:
                                    self.board.teams[other_team_name].current_claims.remove(pos_claim)
                                messages.append(f"Team {other_team_name} lost claim {pos_claim.name} ({pos_claim.type}).")
                    
                    # Remove from possible_claims
                    self.board.possible_claims = self.board.possible_claims[:claim_idx] + self.board.possible_claims[claim_idx+1:]
                    break 
            
            if not target_claim_found:
                messages.append(f"Could not find specified claim '{claim_name_to_acquire}' ({claim_type_to_acquire}) in possible_claims.")

        self.board.teams[team_name].current_card = None
        messages.append(f"Team {team_name}'s current card slot cleared.")
        return messages
