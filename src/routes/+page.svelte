<script lang="ts">
	import { RummyGame } from '$lib';
	import GameContainer from '$lib/game-container.svelte';
	import WelcomeScreen from '$lib/WelcomeScreen.svelte';

	// Game state
	let currentGame = $state<RummyGame | null>(null);
	let playerName = $state('');

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
</script>

{#if currentGame}
	<GameContainer currentGame={currentGame} playerName={playerName} />
{:else}
	<WelcomeScreen onGameStart={handleGameStart} />
{/if}