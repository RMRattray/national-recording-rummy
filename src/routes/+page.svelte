<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { RummyGame } from '$lib';
	import GameContainer from '$lib/game-container.svelte';
	import WelcomeScreen from '$lib/WelcomeScreen.svelte';
	import { io, type Socket } from 'socket.io-client';

	const API_URL = "http://127.0.0.1:5000";

	// Game state
	let currentGame = $state<RummyGame | null>(null);
	let playerName = $state('');
	let playerToken = $state('');
	let players = $state<string[]>([]);
	let selectedPlayers = $state<Set<string>>(new Set());
	let isLoading = $state(false);
	let error = $state('');

	// WebSocket connection
	let socket = $state<Socket | null>(null);

	// Derived values
	let cantStartGame = $derived(isLoading || selectedPlayers.size < 2 || selectedPlayers.size > 4);

	function handleGameStart(gameData: any) {
		// Convert the API response to a RummyGame object
		currentGame = new RummyGame(
			gameData.gameID || 'unknown',
			gameData.playerNames || [],
			gameData.hand || [],
			gameData.handCts || [],
			gameData.melds || [],
			gameData.discards || [],
			gameData.stack || 0,
			gameData.activePlayerName || '',
			gameData.playerCount || 0,
			gameData.eventLog || []
		);
		playerName = gameData.playerName || '';
	}

	function handleGameUpdate(gameData: any) {
		currentGame = new RummyGame(
			gameData.gameID || 'unknown',
			gameData.playerNames || [],
			gameData.hand || [],
			gameData.handCts || [],
			gameData.melds || [],
			gameData.discards || [],
			gameData.stack || 0,
			gameData.activePlayerName || '',
			gameData.playerCount || 0,
			gameData.eventLog || []
		);
	}

	async function makeGameMove(move: string, data: any) {
		const response = await fetch(API_URL + '/game', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				game_id: currentGame?.gameID,
				player_id: playerToken,
				move: move,
				data: data
			})
		});
	}

	async function drawFromStack() {
		await makeGameMove('draw-stack', {});
	}

	async function drawFromDiscard(card: any) {
		await makeGameMove('draw-discard', { card: card });
	}

	async function playMeld(cards: any, meldType: string) {
		await makeGameMove('play-meld', { cards: cards, meld_type: meldType });
	}

	async function discardCard(card: any) {
		await makeGameMove('discard', { card: card });
	}

	async function joinGame(playerNameInput: string) {
		if (!playerNameInput.trim()) {
			error = 'Please enter your name';
			return false;
		}

		isLoading = true;
		error = '';

		try {
			const response = await fetch(API_URL + '/join', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					name: playerNameInput.trim()
				})
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();
			if (data.success) {
				players = data.waiting_players?.map((p: any) => p.name) || [];
				playerToken = data.player_id || '';
				playerName = playerNameInput.trim();
				
				// Auto-select current player when they're added to the list
				if (playerName && players.includes(playerName)) {
					selectedPlayers = new Set([...selectedPlayers, playerName]);
				}

				// Connect to WebSocket and register player
				connectWebSocket();
				return true;
			} else {
				error = data.message || "Failed to join game";
				return false;
			}

		} catch (err) {
			error = 'Failed to join game. Please try again.';
			console.error('Join error:', err);
			return false;
		} finally {
			isLoading = false;
		}
	}

	async function startGame() {
		if (selectedPlayers.size < 2 || selectedPlayers.size > 4 || !playerToken) return false;

		isLoading = true;
		error = '';

		try {
			const response = await fetch(API_URL + '/start-game', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					player_names: Array.from(selectedPlayers)
				})
			});

			if (!response.ok) {
				console.error('Start game error:', response);
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const gameData = await response.json();
			if (gameData.success) {
				return true;
			} else {
				error = gameData.message || "Failed to start game";
				return false;
			}

		} catch (err) {
			error = 'Failed to start game. Please try again.';
			console.error('Start game error:', err);
			return false;
		} finally {
			isLoading = false;
		}
	}

	function connectWebSocket() {
		if (socket || !playerToken) return;

		socket = io(API_URL);

		socket.on('connect', () => {
			console.log('Connected to server');
			// Register this player with the server
			socket?.emit('register_player', { player_id: playerToken });
		});

		socket.on('registered', (data) => {
			console.log('Player registered:', data);
		});

		socket.on('game_started', (data) => {
			console.log('Game started notification:', data);
			if (data.success && data.game_state) {
				handleGameStart(data.game_state);
			}
		});

		socket.on('game_updated', (data) => {
			console.log('Game updated notification:', data);
			if (data.success && data.game_state) {
				handleGameUpdate(data.game_state);
			}
		});

		socket.on('error', (data) => {
			console.error('Socket error:', data);
			error = data.message || 'Connection error';
		});

		socket.on('disconnect', () => {
			console.log('Disconnected from server');
		});
	}

	function disconnectWebSocket() {
		if (socket) {
			socket.disconnect();
			socket = null;
		}
	}

	function togglePlayer(player: string) {
		const newSelectedPlayers = new Set(selectedPlayers);
		if (newSelectedPlayers.has(player)) {
			newSelectedPlayers.delete(player);
		} else {
			newSelectedPlayers.add(player);
		}
		selectedPlayers = newSelectedPlayers; // Trigger reactivity with new Set
	}

	onMount(() => {
		// Connection will be established when player joins
	});

	onDestroy(() => {
		disconnectWebSocket();
	});
</script>

{#if currentGame}
	<GameContainer currentGame={currentGame} playerName={playerName} socket={socket} />
{:else}
	<WelcomeScreen 
		{joinGame}
		{startGame}
		{togglePlayer}
		{players}
		{selectedPlayers}
		{isLoading}
		{error}
		{playerToken}
		{playerName}
		{cantStartGame}
	/>
{/if}