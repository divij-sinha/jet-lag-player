import json
from typing import Optional # Added Optional

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

    def team_travel(self, team_name: str, new_pos_name: str, cost: float = 0.0) -> list[str]:
        messages = []
        team = self.board.teams[team_name]
        
        old_pos_name = None
        if team.current_pos and team.current_pos.name: # Make sure current_pos and its name are not None
            old_pos_name = team.current_pos.name

        # Handle departure from old location
        if old_pos_name and old_pos_name != new_pos_name: # Check if old_pos_name is valid and different from new
            old_location_state = next((loc for loc in self.board.possible_claims if loc.name == old_pos_name), None)
            if old_location_state:
                if team_name in old_location_state.teams_at_location:
                    old_location_state.teams_at_location.remove(team_name)
                    messages.append(f"{team_name} departed from {old_pos_name}.")
                
                if old_location_state.pending_team_name == team_name:
                    old_location_state.pending_team_name = None
                    old_location_state.status = "unclaimed"
                    messages.append(f"{team_name} left {old_pos_name}, abandoning their pending claim. {old_pos_name} is now 'unclaimed'.")
                    # Clear the challenge card if it was for the abandoned claim
                    if team.current_challenge_card and team.current_challenge_card.victory.claim == old_pos_name:
                        team.current_challenge_card = None
                        messages.append(f"{team_name}'s challenge card for {old_pos_name} was cleared.")
            else:
                messages.append(f"Warning: Old position '{old_pos_name}' not found in possible_claims.")


        # Update team's position and budget
        team.current_pos = Position(name=new_pos_name, type="country") # Assuming 'country' type for now
        team.budget -= cost
        messages.append(f"{team_name} traveled to {new_pos_name}. Budget is now {team.budget}.")

        # Handle arrival at new location
        new_location_state = next((loc for loc in self.board.possible_claims if loc.name == new_pos_name), None)
        if new_location_state:
            if team_name not in new_location_state.teams_at_location:
                new_location_state.teams_at_location.append(team_name)
                messages.append(f"{team_name} arrived at {new_pos_name}. Teams here: {', '.join(new_location_state.teams_at_location)}.")
            
            # Report status of the new location
            if new_location_state.status == "unclaimed":
                messages.append(f"{new_pos_name} is unclaimed. {team_name} can attempt the challenge here.")
            elif new_location_state.status == "pending":
                messages.append(f"{new_pos_name} has a pending claim by {new_location_state.pending_team_name}. {team_name} can attempt to contest.")
            elif new_location_state.status == "claimed":
                messages.append(f"{new_pos_name} is already claimed by {new_location_state.claimed_by_team_name}.")
        else:
            messages.append(f"Warning: New position '{new_pos_name}' not found in possible_claims.")
            
        return messages

    def pull_card(self, deck_name: str, team_name: str) -> list[str]:
        return [f"Debug: 'pull_card' for deck '{deck_name}' by team '{team_name}' - this action is likely deprecated or needs redesign for location-specific challenges."]

    def attempt_challenge(self, team_name: str, location_name: Optional[str] = None) -> list[str]:
        messages = []
        team = self.board.teams[team_name]

        if not location_name:
            if team.current_pos and team.current_pos.name:
                location_name = team.current_pos.name
            else:
                messages.append(f"{team_name} has no current position to attempt a challenge.")
                return messages
        
        target_location_state = next((loc for loc in self.board.possible_claims if loc.name == location_name), None)

        if not target_location_state:
            messages.append(f"Location '{location_name}' not found.")
            return messages

        if team_name not in target_location_state.teams_at_location:
            messages.append(f"{team_name} is not at {location_name}.")
            return messages

        if target_location_state.status == "claimed":
            messages.append(f"{location_name} is already permanently claimed by {target_location_state.claimed_by_team_name}.")
            return messages
        
        # Check if team is already working on a different challenge
        if team.current_challenge_card and team.current_challenge_card.victory.claim != location_name:
            messages.append(f"{team_name} is already working on a challenge for {team.current_challenge_card.victory.claim}. Complete or abandon it first.")
            return messages

        # Assign the challenge card
        team.current_challenge_card = target_location_state.challenge_card
        challenge_info = f"Challenge: {team.current_challenge_card.name} - {team.current_challenge_card.challenge}"

        if target_location_state.status == "unclaimed":
            target_location_state.status = "pending"
            target_location_state.pending_team_name = team_name
            messages.append(f"{team_name} is attempting the challenge for {location_name} (new pending claim).")
            messages.append(challenge_info)
        elif target_location_state.status == "pending":
            if target_location_state.pending_team_name != team_name:
                messages.append(f"{team_name} is attempting the challenge for {location_name} (contesting pending claim by {target_location_state.pending_team_name}).")
            else: # Re-attempting own pending challenge
                messages.append(f"{team_name} is re-attempting the challenge for {location_name}.")
            messages.append(challenge_info)
        
        return messages

    def complete_challenge(self, team_name: str) -> list[str]:
        messages = []
        team = self.board.teams[team_name]

        if not team.current_challenge_card:
            messages.append(f"{team_name} has no active challenge card to complete.")
            return messages

        challenge_card_victory_claim = team.current_challenge_card.victory.claim
        target_location_state = next((loc for loc in self.board.possible_claims if loc.name == challenge_card_victory_claim), None)

        if not target_location_state:
            messages.append(f"Error: Location '{challenge_card_victory_claim}' for the completed challenge not found.")
            team.current_challenge_card = None # Clear broken card
            return messages

        # Check if the location is already claimed by another team (e.g. if two teams were contesting)
        if target_location_state.status == "claimed" and target_location_state.claimed_by_team_name != team_name:
            messages.append(f"Unfortunately, {target_location_state.name} was already claimed by {target_location_state.claimed_by_team_name} while {team_name} was attempting the challenge.")
            team.current_challenge_card = None
            return messages

        # Proceed to claim
        target_location_state.status = "claimed"
        target_location_state.claimed_by_team_name = team_name
        target_location_state.pending_team_name = None # Clear any pending status for this location

        team.budget += team.current_challenge_card.card_budget 
        messages.append(f"{team_name} completed the challenge '{team.current_challenge_card.name}' and claimed {target_location_state.name}!")
        messages.append(f"Budget increased by {team.current_challenge_card.card_budget} to {team.budget}.")
        
        team.current_challenge_card = None
        # Also clear the old current_card field for good measure, though it should be deprecated
        if hasattr(team, 'current_card'): team.current_card = None

        return messages
