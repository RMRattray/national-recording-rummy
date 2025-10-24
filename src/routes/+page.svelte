<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { RummyGame, Card, Suit, Value } from '$lib';
	import GameContainer from '$lib/game-container.svelte';
	import WelcomeScreen from '$lib/WelcomeScreen.svelte';

	const API_URL = "https://rummy.nationalrecordingregistry.net";
	// const API_URL = "http://127.0.0.1:5000";

	// Game state
	let currentGame = $state<RummyGame | null>(null);
	let playerName = $state('');
	let playerToken = $state('');
	let players = $state<string[]>([]);
	let selectedPlayers = $state<Set<string>>(new Set());
	let isLoading = $state(false);
	let error = $state('');

	// Derived values
	let cantStartGame = $derived(isLoading || selectedPlayers.size < 2 || selectedPlayers.size > 4);

	$effect(() => console.log(currentGame));

	function convertCardData(cardData: any): Card {
		return new Card(cardData.suit, cardData.value
		);
	}

	function convertCardArray(cardArray: any[]): Card[] {
		return cardArray.map(convertCardData);
	}

	function convertMeldsData(meldsData: any[]): Card[][][] {
		return meldsData.map(playerMelds => 
			playerMelds.map((meld: any) => 
				meld.map(convertCardData)
			)
		);
	}

	function handleGameUpdate(gameData: any) {
		console.log(gameData);
		currentGame = new RummyGame(
			gameData.gameID || 'unknown',
			gameData.playerNames || [],
			convertCardArray(gameData.hand || []),
			gameData.handCts || [],
			convertMeldsData(gameData.melds || []),
			convertCardArray(gameData.discards || []),
			gameData.stack || 0,
			gameData.activePlayerName || '',
			gameData.playerCount || 0,
			gameData.eventLog || []
		);
	}

	function handleGameStateResponse(response: any) {
		if (response['waiting_players']) {
			players = response.waiting_players.map((p: any) => p.name) || [];
		}
		else if (response['game_state']) {
			handleGameUpdate(response['game_state']);
		}
		else console.log(response);
	}

	function startPolling(interval: number = 1000): void {
		setInterval(async() => {
			if (currentGame?.activePlayerName == playerName) return;
			try {
				const response = await fetch(API_URL + "/game_state", {
					method: "POST",
					headers: {
						"Content-Type": "application/json"
					},
					body: JSON.stringify({ player_id : playerToken })
				});
				const data = await response.json();
				handleGameStateResponse(data);
			} catch (error) {
				console.error("Error fetching API:", error);
			}
		}, interval);
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
		const answer = await response.json();
		handleGameStateResponse(answer);
	}

	async function drawFromStack() {
		await makeGameMove('draw-stack', {});
	}

	async function drawFromDiscard(card: any) {
		await makeGameMove('draw-discard', { card: card });
	}

	async function playMeld(cards: any) {
		await makeGameMove('play-meld', { cards: cards });
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

				startPolling();
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

	function togglePlayer(player: string) {
		const newSelectedPlayers = new Set(selectedPlayers);
		if (newSelectedPlayers.has(player)) {
			newSelectedPlayers.delete(player);
		} else {
			newSelectedPlayers.add(player);
		}
		selectedPlayers = newSelectedPlayers; // Trigger reactivity with new Set
	}

	function onExit() {
		const data = JSON.stringify({ player_id: playerToken });
		navigator.sendBeacon(API_URL + "/quit", data);
	}
</script>

<svelte:window on:beforeunload={onExit} />

{#if currentGame}
	<GameContainer 
		currentGame={currentGame} 
		playerName={playerName} 
		{drawFromStack}
		{drawFromDiscard}
		{playMeld}
		{discardCard}
	/>
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