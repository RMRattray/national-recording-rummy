from flask import Flask, request, jsonify
from flask_cors import CORS
from rummy import RummyGame, Card, Suit, Rank, RANK_NAMES
import uuid
from typing import Dict, List, Optional
import json

app = Flask(__name__)
CORS(app)

# Enable CORS for all routes
from flask_cors import cross_origin

# Global game state management
waiting_players: List[Dict[str, str]] = []  # List of waiting players with their IDs and names
active_games: Dict[str, RummyGame] = {}  # Game ID -> RummyGame instance
player_games: Dict[str, str] = {}  # Player ID -> Game ID
player_names: Dict[str, str] = {}  # Player ID -> Player Name
# player_connections: Dict[str, str] = {}  # Player ID -> Socket session ID

def generate_player_id() -> str:
    """Generate a unique player ID."""
    return str(uuid.uuid4())

def generate_game_id() -> str:
    """Generate a unique game ID."""
    return str(uuid.uuid4())

@app.route("/")
def hello_world():
    return "<p>Rummy Game API - Welcome!</p>"

@app.route("/join", methods=["POST"])
@cross_origin()
def join_game():
    """
    Join the waiting room for a game.
    
    Expected JSON:
    {
        "name": "Player Name"
    }
    
    Returns:
    {
        "success": true/false,
        "player_id": "unique_player_id",
        "waiting_players": [{"id": "player_id", "name": "Player Name"}, ...],
        "message": "Success message or error"
    }
    """
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({
                "success": False,
                "message": "Name is required"
            }), 400
        
        player_name = data['name'].strip()
        if not player_name:
            return jsonify({
                "success": False,
                "message": "Name cannot be empty"
            }), 400
        
        # Check if player is already waiting
        for player in waiting_players:
            if player['name'].lower() == player_name.lower():
                return jsonify({
                    "success": False,
                    "message": "A player with this name is already waiting"
                }), 400
        
        # Generate player ID and add to waiting list
        player_id = generate_player_id()
        player_names[player_id] = player_name
        waiting_players.append({
            "id": player_id,
            "name": player_name
        })
        
        return jsonify({
            "success": True,
            "player_id": player_id,
            "waiting_players": waiting_players.copy(),
            "message": f"Successfully joined as {player_name}"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error joining game: {str(e)}"
        }), 500

@app.route("/start-game", methods=["POST"])
@cross_origin()
def start_game():
    """
    Start a new game with the specified players.
    
    Expected JSON:
    {
        "player_names": ["Player1", "Player2", "Player3"]
    }
    
    Returns:
    {
        "success": true/false,
        "game_id": "unique_game_id",
        "game_state": {...},
        "message": "Success message or error"
    }
    """
    try:
        data = request.get_json()
        if not data or 'player_names' not in data:
            return jsonify({
                "success": False,
                "message": "player_names list is required"
            }), 400
        
        player_names_list = data['player_names']
        if not isinstance(player_names_list, list) or len(player_names_list) < 2 or len(player_names_list) > 4:
            return jsonify({
                "success": False,
                "message": "Must specify 2-4 player names"
            }), 400
        
        # Check if all players are in the waiting list
        waiting_player_names = [p['name'] for p in waiting_players]
        missing_players = [name for name in player_names_list if name not in waiting_player_names]
        if missing_players:
            return jsonify({
                "success": False,
                "message": f"Players not found in waiting room: {', '.join(missing_players)}"
            }), 400
        
        # Create the game
        game_id = generate_game_id()
        player_ids = []
        for player_name in player_names_list:
            # Find the player ID for this name
            for player in waiting_players:
                if player['name'] == player_name:
                    player_games[player['id']] = game_id
                    player_ids.append(player['id'])
                    break

        game = RummyGame(len(player_names_list), player_names_list, player_ids)
        active_games[game_id] = game
        
        # Remove players from waiting list
        waiting_players[:] = [p for p in waiting_players if p['name'] not in player_names_list]
        
        # # Notify all players in the game via WebSocket
        # for player_name in player_names_list:
        #     # Find the player ID for this name from the original waiting list
        #     for player_id, name in player_names.items():
        #         if name == player_name and player_id in player_connections:
        #             game_state = get_game_for_player(game_id, player_id)
        #             socketio.emit('game_started', {
        #                 'success': True,
        #                 'game_state': game_state,
        #                 'message': f"Game started with players: {', '.join(player_names_list)}"
        #             }, room=player_connections[player_id])
        #             break
        
        return jsonify({
            "success": True,
            "message": f"Game started with players: {', '.join(player_names_list)}"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error starting game: {str(e)}"
        }), 500

def get_game_for_player(game_id: str, player_id: str) -> Dict:
    """Helper function to get the game state for a specific player."""
    game = active_games[game_id]
    return {
        "gameID": game_id,
        "playerNames": game.player_names,
        "hand": [{"suit": card.suit.value, "value": RANK_NAMES[card.rank.value]} for card in game.players_hands[player_id]],
        "handCts": [len(game.players_hands[i]) for i in game.player_ids],
        "melds": [[[{"suit": card.suit.value, "value": RANK_NAMES[card.rank.value]} for card in meld.cards] for meld in p] for p in [game.players_melds[i] for i in game.player_ids]],
        "discards": [{"suit": card.suit.value, "value": RANK_NAMES[card.rank.value]} for card in game.discard_pile],
        "stack": len(game.stack), 
        "activePlayerName": game.player_names[game.current_player], 
        "playerCount": game.num_players,
        "gameOver": game.is_game_over(),
        "eventLog": game.event_log
    }

@app.route("/game_state", methods=["POST"])
@cross_origin()
def get_game_state() -> Dict:
    try:
        data = request.get_json()
        if not "player_id" in data:
            return jsonify({ "success": False, "message": "no_player_id" })
        player_id = data["player_id"]
        if (player_id in player_games):
            return jsonify({"success": True, "game_state": get_game_for_player(player_games[player_id], player_id)}), 200
        elif (player_id in player_names):
            return jsonify({ "success": True, "waiting_players": waiting_players })
        else:
            return jsonify({ "success": False, "message": f"Invalid player_id: {player_id}" })
    except Exception as e:
        return jsonify({"success": False, "message": f"Aaaauuugh {str(e)}"}), 500



@app.route("/waiting-players", methods=["GET"])
def get_waiting_players():
    """Get list of players waiting for a game."""
    return jsonify({
        "success": True,
        "waiting_players": waiting_players
    })

@app.route("/game", methods=["POST"])
@cross_origin()
def game_move():
    """Handle a game move."""
    try:
        data = request.get_json()
        if not data or 'game_id' not in data or 'player_id' not in data or 'move' not in data:
            return jsonify({"success": False, "message": "game_id, player_id, and move are required"}), 400
        game_id = data['game_id']
        game = active_games[game_id]
        if game is None:
            return jsonify({"success": False, "message": "Game not found"}), 400
        player_id = data['player_id']
        move = data['move']
        if move == "draw-stack":
            game.draw_from_stack(player_id)
        elif move == "draw-discard":
            card = Card(suit=Suit(data['data']['card']['suit']), rank=Rank(RANK_NAMES.index(data['data']['card']['value'])))
            game.draw_from_discard(player_id, card)
        elif move == "play-meld":
            cards = [Card(suit=Suit(card['suit']), rank=Rank(RANK_NAMES.index(card['value']))) for card in data['data']['cards']]
            game.play_meld(player_id, cards)
        elif move == "discard":
            card = Card(suit=Suit(data['data']['card']['suit']), rank=Rank(RANK_NAMES.index(data['data']['card']['value'])))
            game.discard_card(player_id, card)
        # for player_id in game.player_ids:
        #     game_state = get_game_for_player(game_id, player_id)
        #     socketio.emit('game_updated', {
        #         'success': True,
        #         'game_state': get_game_for_player(game_id, player_id)
        #     }, room=player_connections[player_id])
        return jsonify({"success": True, "game_state": get_game_for_player(game_id, player_id)}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error handling game move: {str(e)}"}), 500
