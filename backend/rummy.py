import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class Suit(Enum):
    """Card suits in a standard deck."""
    HEARTS = "hearts"
    DIAMONDS = "diamonds"
    CLUBS = "clubs"
    SPADES = "spades"


class Rank(Enum):
    """Card ranks in a standard deck."""
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13

class MeldType(Enum):
    NONE = 0
    SET = 1
    RUN = 2

RANK_NAMES = ['','A','2','3','4','5','6','7','8','9','10','J','Q','K']
MELD_TYPE_NAMES = ['NONE','SET','RUN']

@dataclass
class Card:
    """Represents a playing card."""
    suit: Suit
    rank: Rank
    meld_type: MeldType
    
    def __str__(self) -> str:
        return f"{self.rank.name.lower()} of {self.suit.value}"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank and self.meld_type == other.meld_type
    
    def __hash__(self) -> int:
        return hash((self.suit, self.rank))

@dataclass
class Meld:
    """Represents a meld (set or run) of cards."""
    cards: List[Card]
    meld_type: MeldType 

def forms_meld(cards: List[Card]) -> MeldType:
    if (len(cards) < 3):
        return MeldType.NONE 
    
    rank = cards[0].rank 
    if all(card.rank == rank and card.meld_type != MeldType.RUN for card in cards):
        return MeldType.SET
    
    suit = cards[0].suit 
    if not all(card.suit == suit and card.meld_type != MeldType.SET for card in cards):
        return MeldType.NONE
    
    ranks = sorted([card.rank.value for card in cards])
    for i in range(1, len(ranks)):
        if (not ((ranks[i] == ranks[i - 1] + 1) or (i == 1 and ranks[0] == 1 and ranks[-1] == 13))):
            return MeldType.NONE
    
    return MeldType.RUN


class RummyGame:
    """A complete Rummy game implementation."""
    
    def __init__(self, num_players: int, player_names: List[str], player_ids: List[str]):
        """
        Initialize a new Rummy game.
        
        Args:
            num_players: Number of players (2-4)
            player_names: Optional list of player names. If not provided, 
                         names will be "Player 1", "Player 2", etc.
        
        Raises:
            ValueError: If num_players is not between 2 and 4
        """
        if not 2 <= num_players <= 4:
            raise ValueError("Number of players must be between 2 and 4")
        
        self.num_players = num_players
        self.player_names = player_names or [f"Player {i+1}" for i in range(num_players)]
        self.player_ids = player_ids
        
        if len(self.player_names) != num_players or len(self.player_ids) != num_players:
            raise ValueError("Number of player names and IDs must match number of players")

        
        # Initialize game state
        self.players_hands: Dict[str, List[Card]] = {}
        self.players_melds: Dict[str, List[Meld]] = {}
        self.stack: List[Card] = []
        self.discard_pile: List[Card] = []
        self.current_player = 0
        self.current_player_has_drawn = False
        self.round = 0
        self.game_over = False
        self.winner = None
        self.scores: Dict[str, int] = {}
        for pid in player_ids:
            self.scores[pid] = 0
        self.event_log: List[str] = []
        
        # Create and shuffle deck
        self._create_deck()

        self._deal_cards()
    
    def _create_deck(self) -> None:
        """Create a standard 52-card deck and shuffle it."""
        self.stack = []
        for suit in Suit:
            for rank in Rank:
                self.stack.append(Card(suit, rank, MeldType.NONE))
        random.shuffle(self.stack)
    
    def _deal_cards(self) -> None:
        """Deal 10 cards to each player."""
        for player_id in self.player_ids:
            self.players_hands[player_id] = []
            self.players_melds[player_id] = []
        
        # Deal 10 cards to each player
        for _ in range(10):
            for player_id in self.player_ids:
                if self.stack:
                    card = self.stack.pop()
                    self.players_hands[player_id].append(card)
        for each in self.players_hands.values():
            each.sort(key=lambda x: x.rank.value)

        # Put one card on the discard pile to start
        self.discard_pile = []
        if self.stack:
            self.discard_pile.append(self.stack.pop())
    
    def draw_from_stack(self, player_id: int) -> Optional[Card]:
        """
        Draw a card from the stack.
        
        Args:
            player_id: ID of the player drawing the card
            
        Returns:
            The drawn card, or None if stack is empty
            
        Raises:
            ValueError: If player_id is invalid
        """
        if player_id not in self.player_ids:
            raise ValueError(f"Invalid player ID: {player_id}")
        
        if not self.stack:
            return None
        
        if self.current_player_has_drawn:
            self.event_log.append(f"{self.player_names[self.player_ids.index(player_id)]} attempted to draw from the stack after having already drawn")
            return None
        
        card = self.stack.pop()
        self.players_hands[player_id].append(card)
        self.event_log.append(f"{self.player_names[self.player_ids.index(player_id)]} drew a card from the stack")
        self.current_player_has_drawn = True
        return card
    
    def draw_from_discard(self, player_id: int, card: Card) -> bool:
        """
        Draw a specific card from the discard pile.
        
        Args:
            player_id: ID of the player drawing the card
            card: The specific card to draw
            
        Returns:
            True if the card was successfully drawn, False otherwise
            
        Raises:
            ValueError: If player_id is invalid
        """
        if player_id not in self.player_ids:
            raise ValueError(f"Invalid player ID: {player_id}")
        
        if not self.discard_pile:
            return False
        
        if self.current_player_has_drawn:
            self.event_log.append(f"{self.player_names[self.player_ids.index(player_id)]} attempted to draw from the discard pile after having already drawn")
            return None
        
        # Find the card in the discard pile
        try:
            card_index = self.discard_pile.index(card)
            drawn_cards = self.discard_pile[card_index:]
            self.discard_pile = self.discard_pile[:card_index]
            self.players_hands[player_id] += drawn_cards
            match len(drawn_cards):
                case 1:
                    self.event_log.append(f"{self.player_names[self.player_ids.index(player_id)]} drew the {drawn_cards[0]} from the discard pile")
                case 2:
                    self.event_log.append(f"{self.player_names[self.player_ids.index(player_id)]} drew the {drawn_cards[0]} and the {drawn_cards[1]} from the discard pile")
                case 3:
                    self.event_log.append(f"{self.player_names[self.player_ids.index(player_id)]} drew the {drawn_cards[0]}, the {drawn_cards[1]}, and the {drawn_cards[2]} from the discard pile")
                case _:
                    self.event_log.append(f"{self.player_names[self.player_ids.index(player_id)]} drew {len(drawn_cards)} cards from the discard pile, beginning with the {drawn_cards[0]}")
            self.current_player_has_drawn = True
            return True
        except ValueError:
            return False
    
    def play_meld(self, player_id: int, cards: List[Card]) -> bool:
        """
        Play a meld (set or run) of cards.
        
        Args:
            player_id: ID of the player playing the meld
            cards: List of cards to form the meld
            meld_type: Type of meld ("set" or "run")
            
        Returns:
            True if the meld was successfully played, False otherwise
            
        Raises:
            ValueError: If player_id is invalid or meld_type is invalid
        """
        if player_id not in self.player_ids:
            raise ValueError(f"Invalid player ID: {player_id}")
        
        # Check if all cards are in player's hand or existing melds
        player_hand = self.players_hands[player_id]
        existing_melds = [c for melds in self.players_melds.values() for m in melds for c in m.cards]
        for card in cards:
            if card.meld_type == MeldType.NONE:
                if card not in player_hand:
                    return False
            else:
                if card not in existing_melds:
                    return False
        
        # Check if cards form valid meld
        meld_type = forms_meld(cards)
        if meld_type == MeldType.NONE:
            self.event_log.append(f"{self.player_names[self.player_ids.index(player_id)]} attempted to play an invalid meld")
            return False
        
        # Remove cards from player's hand and add to player's melds
        cards.sort(key=lambda x: x.rank.value) # sort meld
        meld = Meld([], meld_type)
        allNewCards = True
        for card in cards:
            if card in player_hand:
                player_hand.remove(card)
                card.meld_type = meld_type
                meld.cards.append(card)
            else:
                allNewCards = False
        
        self.players_melds[player_id].append(meld)
        meld_cards_info = f"{len(meld.cards)} card{'s' if len(meld.cards) > 1 else ''}"
        self.event_log.append(f"{self.player_names[self.player_ids.index(player_id)]} {f'played a {MELD_TYPE_NAMES[meld.meld_type.value]} of {meld_cards_info}' if allNewCards else f'added {meld_cards_info} to a {MELD_TYPE_NAMES[meld.meld_type.value]}'}")
        # Check if player's hand is empty (game end condition)
        if len(player_hand) == 0:
            self.event_log.append(f"{self.player_names[self.player_ids.index(player_id)]} is out of cards!")
            self._end_game()
        
        return True
    
    def discard_card(self, player_id: int, card: Card) -> bool:
        """
        Discard a card from a player's hand to the discard pile.
        This action ends the player's turn.
        
        Args:
            player_id: ID of the player discarding the card
            card: The card to discard
            
        Returns:
            True if the card was successfully discarded, False otherwise
            
        Raises:
            ValueError: If player_id is invalid
        """
        if player_id not in self.player_ids:
            raise ValueError(f"Invalid player ID: {player_id}")
        
        player_hand = self.players_hands[player_id]
        if card not in player_hand:
            return False
        
        if not self.current_player_has_drawn:
            self.event_log.append(f"{self.player_names[self.player_ids.index(player_id)]} attempted to discard before drawing a card")
            return True
        
        # Remove card from player's hand and add to discard pile
        player_hand.remove(card)
        player_hand.sort(key=lambda x: x.rank.value)
        self.discard_pile.append(card)
        self.event_log.append(f"{self.player_names[self.player_ids.index(player_id)]} discarded the {card}")
        # Check if player's hand is empty (game end condition)
        if len(player_hand) == 0:
            self.event_log.append(f"{self.player_names[self.player_ids.index(player_id)]} is out of cards!")
            self._end_game()
        else:
            # End the turn (move to next player)
            self.end_turn()
        
        return True
    
    def sort_hand(self, player_id: int):
        player_hand = self.players_hands[player_id]
        player_hand.sort(key=lambda x: x.rank.value)
    
    def get_player_hand(self, player_id: int) -> List[Card]:
        """
        Get a copy of a player's hand.
        
        Args:
            player_id: ID of the player
            
        Returns:
            List of cards in the player's hand
            
        Raises:
            ValueError: If player_id is invalid
        """
        if player_id not in self.player_ids:
            raise ValueError(f"Invalid player ID: {player_id}")
        
        return self.players_hands[player_id].copy()
    
    def get_stack_size(self) -> int:
        """Get the number of cards remaining in the stack."""
        return len(self.stack)
    
    def get_discard_pile(self) -> List[Card]:
        """Get a copy of the discard pile."""
        return self.discard_pile.copy()
    
    def get_top_discard(self) -> Optional[Card]:
        """Get the top card of the discard pile without removing it."""
        return self.discard_pile[-1] if self.discard_pile else None
    
    def get_player_name(self, player_id: int) -> str:
        """
        Get the name of a player.
        
        Args:
            player_id: ID of the player
            
        Returns:
            The player's name
            
        Raises:
            ValueError: If player_id is invalid
        """
        if player_id not in self.player_ids:
            raise ValueError(f"Invalid player ID: {player_id}")
        
        return self.player_names[player_id]
    
    def get_all_player_info(self) -> List[Dict[str, any]]:
        """
        Get information about all players.
        
        Returns:
            List of dictionaries containing player info
        """
        return [
            {
                "id": player_id,
                "name": self.player_names[player_id],
                "hand_size": len(self.players_hands[player_id])
            }
            for player_id in self.player_ids
        ]
    
    def check_win_condition(self, player_id: int) -> bool:
        """
        Check if a player has won (empty hand).
        
        Args:
            player_id: ID of the player to check
            
        Returns:
            True if the player has won, False otherwise
        """
        if player_id not in self.player_ids:
            return False
        
        return len(self.players_hands[player_id]) == 0
    
    def _calculate_card_points(self, card: Card) -> int:
        """
        Calculate points for a single card.
        
        Args:
            card: The card to calculate points for
            
        Returns:
            Points for the card (15 for ace, 10 for face cards, 5 for number cards)
        """
        if card.rank == Rank.ACE:
            return 15
        elif card.rank in [Rank.JACK, Rank.QUEEN, Rank.KING]:
            return 10
        else:
            return 5
    
    def _calculate_player_score(self, player_id: int) -> int:
        """
        Calculate the score for a player.
        
        Args:
            player_id: ID of the player to calculate score for
            
        Returns:
            The player's score (positive for melds, negative for remaining hand)
        """
        score = 0
        
        # Add points for cards in melds
        for meld in self.players_melds[player_id]:
            for card in meld.cards:
                score += self._calculate_card_points(card)
        
        # Subtract points for cards remaining in hand
        for card in self.players_hands[player_id]:
            score -= self._calculate_card_points(card)
        
        return score
    
    def _end_game(self) -> None:
        """End the game and calculate final scores."""
        self.game_over = True
        
        # Calculate scores for all players
        over_500 = False
        for player_id in self.player_ids:
            round_score = self._calculate_player_score(player_id)
            name = self.player_names[self.player_ids.index(player_id)]
            self.scores[player_id] += round_score
            self.event_log.append(f"{name} gets {round_score} points, for a total of {self.scores[player_id]}")
            if (self.scores[player_id] > 500):
                over_500 = True
 
        
        if (not over_500):
            self.event_log.append("No one has over 500 points - play continues")
            # Create and shuffle deck
            self._create_deck()

            self._deal_cards()

            self.end_turn()

            # End round (make separate function?)
            self.round += 1
            self.current_player = self.round % self.num_players
        
        else:
            # Find the winner (highest score)
            self.winner = self.player_names[self.player_ids.index(max(self.player_ids, key=lambda pid: self.scores[pid]))]
            self.event_log.append(f"{self.winner} wins!")
    
    def end_turn(self) -> None:
        """End the current player's turn and move to the next player."""
        self.current_player_has_drawn = False
        self.current_player = (self.current_player + 1) % self.num_players
    
    def get_current_player(self) -> int:
        """Get the ID of the current player."""
        return self.player_ids[self.current_player]
    
    def is_game_over(self) -> bool:
        """Check if the game is over."""
        return self.game_over
    
    def get_winner(self) -> Optional[int]:
        """Get the ID of the winner, or None if no winner yet."""
        return self.winner
    
    def get_player_melds(self, player_id: int) -> List[Meld]:
        """
        Get a copy of a player's melds.
        
        Args:
            player_id: ID of the player
            
        Returns:
            List of melds played by the player
            
        Raises:
            ValueError: If player_id is invalid
        """
        if player_id not in self.player_ids:
            raise ValueError(f"Invalid player ID: {player_id}")
        
        return self.players_melds[player_id].copy()
    
    def get_player_score(self, player_id: int) -> int:
        """
        Get a player's current score.
        
        Args:
            player_id: ID of the player
            
        Returns:
            The player's current score
            
        Raises:
            ValueError: If player_id is invalid
        """
        if player_id not in self.player_ids:
            raise ValueError(f"Invalid player ID: {player_id}")
        
        return self.scores[player_id]
    
    def get_all_scores(self) -> Dict[int, int]:
        """Get all players' scores."""
        return self.scores.copy()
    
    def get_final_results(self) -> Optional[List[Dict[str, any]]]:
        """
        Get final game results if the game is over.
        
        Returns:
            List of dictionaries with player results, or None if game not over
        """
        if not self.game_over:
            return None
        
        results = []
        for player_id in self.player_ids:
            results.append({
                "player_id": player_id,
                "name": self.get_player_name(player_id),
                "score": self.scores[player_id],
                "is_winner": player_id == self.winner
            })
        
        # Sort by score (highest first)
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def __str__(self) -> str:
        """String representation of the game state."""
        result = f"Rummy Game - {self.num_players} players\n"
        result += f"Stack: {len(self.stack)} cards\n"
        result += f"Discard pile: {len(self.discard_pile)} cards\n"
        result += f"Current player: {self.get_player_name(self.current_player)}\n"
        result += f"Game over: {self.game_over}\n\n"
        
        for player_id in self.player_ids:
            hand_size = len(self.players_hands[player_id])
            melds_count = len(self.players_melds[player_id])
            score = self.scores[player_id]
            result += f"{self.get_player_name(player_id)}: {hand_size} cards, {melds_count} melds, score: {score}\n"
        
        if self.game_over and self.winner is not None:
            result += f"\nWinner: {self.get_player_name(self.winner)} (Score: {self.scores[self.winner]})\n"
        
        return result
