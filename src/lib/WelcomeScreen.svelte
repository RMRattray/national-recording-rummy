<script lang="ts">
	import { onDestroy } from 'svelte';

	export let onGameStart: (gameData: any) => void;

	let playerName = '';
	let playerToken = '';
	let players: string[] = [];
	let selectedPlayers: Set<string> = new Set();
	let isLoading = false;
	let error = '';
	let pollingInterval: number | null = null;

	// Auto-select current player when they're added to the list
	$: if (playerName && players.includes(playerName)) {
		selectedPlayers.add(playerName);
	}

	// Check if start game button should be enabled
	$: canStartGame = selectedPlayers.size >= 2 && selectedPlayers.size <= 4;

	async function joinGame() {
		if (!playerName.trim()) {
			error = 'Please enter your name';
			return;
		}

		isLoading = true;
		error = '';

		try {
			const response = await fetch('https://example.com/backend', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					request_type: 'join',
					name: playerName.trim()
				})
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();
			players = data.players || [];
			playerToken = data.playerToken || '';

			// Start polling for game start
			startPolling();

		} catch (err) {
			error = 'Failed to join game. Please try again.';
			console.error('Join error:', err);
		} finally {
			isLoading = false;
		}
	}

	async function startGame() {
		if (!canStartGame || !playerToken) return;

		isLoading = true;
		error = '';

		try {
			const response = await fetch('https://example.com/backend', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					request_type: 'start_game',
					playerToken: playerToken,
					selectedPlayers: Array.from(selectedPlayers)
				})
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const gameData = await response.json();
			stopPolling();
			onGameStart(gameData);

		} catch (err) {
			error = 'Failed to start game. Please try again.';
			console.error('Start game error:', err);
		} finally {
			isLoading = false;
		}
	}

	function startPolling() {
		if (pollingInterval) return;

		pollingInterval = setInterval(async () => {
			if (!playerToken) return;

			try {
				const response = await fetch('https://example.com/backend', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify({
						request_type: 'is_game_started',
						playerToken: playerToken
					})
				});

				if (response.ok) {
					const data = await response.json();
					if (data.gameStarted && data.gameData) {
						stopPolling();
						onGameStart(data.gameData);
					}
				}
			} catch (err) {
				console.error('Polling error:', err);
			}
		}, 1000);
	}

	function stopPolling() {
		if (pollingInterval) {
			clearInterval(pollingInterval);
			pollingInterval = null;
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

	onDestroy(() => {
		stopPolling();
	});
</script>

<div class="welcome-container">
	<div class="welcome-card">
		<h1>National Recording Rummy</h1>
		
		{#if !playerToken}
			<!-- Join form -->
			<div class="join-section">
				<h2>Join Game</h2>
				<div class="input-group">
					<label for="playerName">Your Name:</label>
					<input 
						id="playerName"
						type="text" 
						bind:value={playerName} 
						placeholder="Enter your name"
						disabled={isLoading}
					/>
				</div>
				<button 
					class="join-button" 
					on:click={joinGame}
					disabled={isLoading || !playerName.trim()}
				>
					{isLoading ? 'Joining...' : 'Join Game'}
				</button>
			</div>
		{:else}
			<!-- Player selection and game start -->
			<div class="game-setup-section">
				<h2>Select Players</h2>
				<p class="instruction">Choose 2-4 players to start the game:</p>
				
				<div class="players-list">
					{#each players as player}
						<label class="player-option">
							<input 
								type="checkbox"
								checked={selectedPlayers.has(player)}
								on:change={() => togglePlayer(player)}
								disabled={player === playerName}
							/>
							<span class="player-name" class:current={player === playerName}>
								{player} {player === playerName ? '(You)' : ''}
							</span>
						</label>
					{/each}
				</div>

				<div class="game-controls">
					<p class="selection-info">
						{selectedPlayers.size} player{selectedPlayers.size !== 1 ? 's' : ''} selected
						{#if selectedPlayers.size < 2}
							(Need at least 2)
						{:else if selectedPlayers.size > 4}
							(Maximum 4 allowed)
						{/if}
					</p>
					
					<button 
						class="start-button" 
						on:click={startGame}
						disabled={isLoading || !canStartGame}
					>
						{isLoading ? 'Starting...' : 'Start Game'}
					</button>
				</div>
			</div>
		{/if}

		{#if error}
			<div class="error-message">
				{error}
			</div>
		{/if}
	</div>
</div>

<style>
	.welcome-container {
		height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, #0f4c3a, #1a5f3f);
		padding: 2rem;
	}

	.welcome-card {
		background: rgba(0, 0, 0, 0.8);
		border-radius: 12px;
		padding: 3rem;
		max-width: 500px;
		width: 100%;
		border: 2px solid #2d7a5f;
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
	}

	h1 {
		text-align: center;
		color: #90EE90;
		font-size: 2.5rem;
		margin: 0 0 2rem 0;
		font-weight: bold;
	}

	h2 {
		text-align: center;
		color: #90EE90;
		font-size: 1.5rem;
		margin: 0 0 1.5rem 0;
	}

	.join-section, .game-setup-section {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.input-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	label {
		color: #90EE90;
		font-weight: bold;
		font-size: 1.1rem;
	}

	input[type="text"] {
		padding: 0.75rem;
		border: 2px solid #2d7a5f;
		border-radius: 6px;
		background: rgba(255, 255, 255, 0.1);
		color: white;
		font-size: 1rem;
	}

	input[type="text"]:focus {
		outline: none;
		border-color: #90EE90;
		box-shadow: 0 0 8px rgba(144, 238, 144, 0.3);
	}

	input[type="text"]::placeholder {
		color: rgba(255, 255, 255, 0.6);
	}

	.join-button, .start-button {
		padding: 1rem 2rem;
		background: linear-gradient(135deg, #2d7a5f, #1a5f3f);
		border: 2px solid #90EE90;
		border-radius: 8px;
		color: white;
		font-size: 1.2rem;
		font-weight: bold;
		cursor: pointer;
		transition: all 0.3s ease;
	}

	.join-button:hover:not(:disabled), .start-button:hover:not(:disabled) {
		background: linear-gradient(135deg, #90EE90, #2d7a5f);
		transform: translateY(-2px);
		box-shadow: 0 4px 16px rgba(144, 238, 144, 0.3);
	}

	.join-button:disabled, .start-button:disabled {
		opacity: 0.6;
		cursor: not-allowed;
		transform: none;
		box-shadow: none;
	}

	.instruction {
		text-align: center;
		color: rgba(255, 255, 255, 0.8);
		font-size: 1rem;
		margin: 0;
	}

	.players-list {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.player-option {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.75rem;
		background: rgba(255, 255, 255, 0.1);
		border-radius: 6px;
		border: 2px solid transparent;
		cursor: pointer;
		transition: all 0.3s ease;
	}

	.player-option:hover {
		background: rgba(255, 255, 255, 0.15);
		border-color: #2d7a5f;
	}

	input[type="checkbox"] {
		width: 18px;
		height: 18px;
		accent-color: #90EE90;
	}

	.player-name {
		color: white;
		font-size: 1.1rem;
		flex: 1;
	}

	.player-name.current {
		color: #90EE90;
		font-weight: bold;
	}

	.game-controls {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		align-items: center;
	}

	.selection-info {
		color: rgba(255, 255, 255, 0.8);
		font-size: 1rem;
		margin: 0;
		text-align: center;
	}

	.error-message {
		background: rgba(220, 53, 69, 0.2);
		border: 2px solid #dc3545;
		border-radius: 6px;
		padding: 1rem;
		color: #ff6b7a;
		text-align: center;
		font-weight: bold;
		margin-top: 1rem;
	}

	/* Responsive design */
	@media (max-width: 600px) {
		.welcome-container {
			padding: 1rem;
		}
		
		.welcome-card {
			padding: 2rem;
		}
		
		h1 {
			font-size: 2rem;
		}
		
		h2 {
			font-size: 1.3rem;
		}
	}
</style>
