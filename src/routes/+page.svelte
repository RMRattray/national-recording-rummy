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
					selectedPlayers.add(playerName);
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
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const gameData = await response.json();
			if (gameData.success) {
				handleGameStart(gameData.game_state);
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
		if (selectedPlayers.has(player)) {
			selectedPlayers.delete(player);
		} else {
			selectedPlayers.add(player);
		}
		selectedPlayers = selectedPlayers; // Trigger reactivity
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
	/>
{/if}