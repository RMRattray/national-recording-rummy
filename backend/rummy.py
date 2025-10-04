import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class Suit(Enum):
    """Card suits in a standard deck."""
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"
    SPADES = "Spades"


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


@dataclass
class Card:
    """Represents a playing card."""
    suit: Suit
    rank: Rank
    
    def __str__(self) -> str:
        return f"{self.rank.name} of {self.suit.value}"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank
    
    def __hash__(self) -> int:
        return hash((self.suit, self.rank))


@dataclass
class Meld:
    """Represents a meld (set or run) of cards."""
    cards: List[Card]
    meld_type: str  # "set" or "run"
    
    def is_valid(self) -> bool:
        """Check if the meld is valid according to rummy rules."""
        if len(self.cards) < 3:
            return False
        
        if self.meld_type == "set":
            # All cards must have the same rank
            rank = self.cards[0].rank
            return all(card.rank == rank for card in self.cards)
        elif self.meld_type == "run":
            # All cards must be same suit and consecutive ranks
            suit = self.cards[0].suit
            ranks = sorted([card.rank.value for card in self.cards])
            
            if not all(card.suit == suit for card in self.cards):
                return False
            
            # Check if ranks are consecutive
            for i in range(1, len(ranks)):
                if ranks[i] != ranks[i-1] + 1:
                    return False
            
            return True
        
        return False


class RummyGame:
    """A complete Rummy game implementation."""
    
    def __init__(self, num_players: int, player_names: Optional[List[str]] = None):
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
        self.player_ids = list(range(num_players))
        
        if len(self.player_names) != num_players:
            raise ValueError("Number of player names must match number of players")
        
        # Initialize game state
        self.players_hands: Dict[int, List[Card]] = {}
        self.players_melds: Dict[int, List[Meld]] = {}
        self.stack: List[Card] = []
        self.discard_pile: List[Card] = []
        self.current_player = 0
        self.game_over = False
        self.winner = None
        self.scores: Dict[int, int] = {}
        
        # Create and shuffle deck
        self._create_deck()
        self._deal_cards()
    
    def _create_deck(self) -> None:
        """Create a standard 52-card deck and shuffle it."""
        self.stack = []
        for suit in Suit:
            for rank in Rank:
                self.stack.append(Card(suit, rank))
        random.shuffle(self.stack)
    
    def _deal_cards(self) -> None:
        """Deal 10 cards to each player."""
        for player_id in self.player_ids:
            self.players_hands[player_id] = []
            self.players_melds[player_id] = []
            self.scores[player_id] = 0
        
        # Deal 10 cards to each player
        for _ in range(10):
            for player_id in self.player_ids:
                if self.stack:
                    card = self.stack.pop()
                    self.players_hands[player_id].append(card)
        
        # Put one card on the discard pile to start
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
        
        card = self.stack.pop()
        self.players_hands[player_id].append(card)
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
        
        # Find the card in the discard pile
        try:
            card_index = self.discard_pile.index(card)
            drawn_card = self.discard_pile.pop(card_index)
            self.players_hands[player_id].append(drawn_card)
            return True
        except ValueError:
            return False
    
    def play_meld(self, player_id: int, cards: List[Card], meld_type: str) -> bool:
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
        
        if meld_type not in ["set", "run"]:
            raise ValueError("Meld type must be 'set' or 'run'")
        
        # Check if player has all the cards
        player_hand = self.players_hands[player_id]
        for card in cards:
            if card not in player_hand:
                return False
        
        # Create and validate the meld
        meld = Meld(cards, meld_type)
        if not meld.is_valid():
            return False
        
        # Remove cards from player's hand and add to player's melds
        for card in cards:
            player_hand.remove(card)
        
        self.players_melds[player_id].append(meld)
        
        # Check if player's hand is empty (game end condition)
        if len(player_hand) == 0:
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
        
        # Remove card from player's hand and add to discard pile
        player_hand.remove(card)
        self.discard_pile.append(card)
        
        # Check if player's hand is empty (game end condition)
        if len(player_hand) == 0:
            self._end_game()
        else:
            # End the turn (move to next player)
            self.end_turn()
        
        return True
    
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
        for player_id in self.player_ids:
            self.scores[player_id] = self._calculate_player_score(player_id)
        
        # Find the winner (highest score)
        self.winner = max(self.player_ids, key=lambda pid: self.scores[pid])
    
    def end_turn(self) -> None:
        """End the current player's turn and move to the next player."""
        self.current_player = (self.current_player + 1) % self.num_players
    
    def get_current_player(self) -> int:
        """Get the ID of the current player."""
        return self.current_player
    
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
