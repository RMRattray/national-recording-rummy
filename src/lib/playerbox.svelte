<script lang="ts">
	import { RummyGame, Card, Suit, Value } from '$lib';
	import CardBox from '$lib/cardbox.svelte';

    let { game, playerIndex, vertical, lefttop, user }: { game: RummyGame, playerIndex: number, vertical: boolean, lefttop: boolean, user: boolean } = $props();

	// Get player name
	let playerName = $derived(game.playerNames[playerIndex] || 'Unknown Player');
	
	// Get hand count for this player
	let handCount = $derived(game.handCts[playerIndex] || 0);
	
	// Get melds for this player
	let playerMelds = $derived(game.melds[playerIndex]);
	
	// Get hand for this player (only if it's the current user)
	let playerHand = $derived(user ? game.hand : []);
	
	// Check if this player is the active player
	let active = $derived(game.activePlayerName === playerName);
</script>

<div 
	class="player-container" 
	class:vertical 
	class:active
	class:user
>
	<div class="player-info">
		<span class="player-name">{playerName}{user ? ' (You)' : ''}, index: {playerIndex}</span>
		<span class="card-count">({user ? playerHand.length : handCount} cards)</span>
	</div>
	
	<div class="player-area" class:vertical>
		<!-- Melds -->
		<div class="melds">
			{#each playerMelds as meld}
				{#each meld as card}
					<CardBox card={card} revealed={true} />
				{/each}
			{/each}
		</div>
		
		<!-- Hand -->
		<div class="player-hand">
			{#if user}
				<!-- Show actual hand for current user -->
				{#each playerHand as card}
					<CardBox card={card} revealed={true} />
				{/each}
			{:else}
				<!-- Show hidden cards for other players -->
				{#each Array(handCount) as _, i}
					<CardBox card={new Card(Suit.SPADES, Value.ACE)} revealed={false} />
				{/each}
			{/if}
		</div>
	</div>
</div>

<style>
	.player-container {
		background: rgba(0, 0, 0, 0.3);
		border-radius: 6px;
		padding: 0.5rem;
		border: 2px solid transparent;
		transition: all 0.3s ease;
		display: flex;
		flex-direction: column;
		min-height: 80px;
	}

	.player-container.vertical {
		min-width: 150px;
		max-width: 200px;
	}

	.player-container.active {
		border-color: #FFD700;
		background: rgba(255, 215, 0, 0.1);
		box-shadow: 0 0 8px rgba(255, 215, 0, 0.3);
	}

	.player-container.user {
		border: 2px solid #2d7a5f;
	}

	.player-info {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.5rem;
		font-size: 0.8rem;
	}

	.player-name {
		font-weight: bold;
		color: #90EE90;
	}

	.card-count {
		font-size: 0.7rem;
		opacity: 0.8;
	}

	.player-area {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		flex: 1;
	}

	.player-area.vertical {
		align-items: center;
	}

	.melds {
		display: flex;
		gap: 0.2rem;
		flex-wrap: wrap;
		justify-content: center;
		margin-bottom: 0.5rem;
	}

	.player-hand {
		display: flex;
		gap: 0.1rem;
		flex-wrap: wrap;
		justify-content: center;
	}

	/* Responsive adjustments */
	@media (max-width: 800px) {
		.player-container.vertical {
			min-width: 100px;
			max-width: 110px;
		}
	}
</style>
