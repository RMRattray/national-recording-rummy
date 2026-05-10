<script lang="ts">
	import { Card, Suit, Rank } from '$lib';
    let { card, revealed }: { card: Card, revealed: boolean } = $props();

    // Helper function to get card color
	function getCardColor(suit: Suit): string {
		return suit === Suit.HEARTS || suit === Suit.DIAMONDS ? 'red' : 'black';
	}

	// Helper function to get suit symbol
	function getSuitSymbol(suit: Suit): string {
		switch (suit) {
			case Suit.HEARTS: return '♥';
			case Suit.DIAMONDS: return '♦';
			case Suit.CLUBS: return '♣';
			case Suit.SPADES: return '♠';
		}
	}

	// Helper function to get rank symbol
	function getRankSymbol(rank: Rank): string {
		console.log(rank);
		switch (rank) {
			case Rank.ACE: return 'A';
			case Rank.TWO: return '2';
			case Rank.THREE: return '3';
			case Rank.FOUR: return '4';
			case Rank.FIVE: return '5';
			case Rank.SIX: return '6';
			case Rank.SEVEN: return '7';
			case Rank.EIGHT: return '8';
			case Rank.NINE: return '9';
			case Rank.TEN: return '10';
			case Rank.JACK: return 'J';
			case Rank.QUEEN: return 'Q';
			case Rank.KING: return 'K';
			case Rank.HIGH_ACE: return 'A';
		}
	}
</script>

<div class="card" class:revealed-card={revealed} class:hidden-card={!revealed}>
    {#if revealed}
        <div class="card-top" style="color: {getCardColor(card.suit)}">
            <span class="suit"></span>
            <span class="value">{getRankSymbol(card.rank)}</span>
        </div>
        <div class="card-center" style="color: {getCardColor(card.suit)}">
            <span class="suit-large">{getSuitSymbol(card.suit)}</span>
        </div>
    {:else}
        <div class="card-back">🂠</div>
    {/if}
</div>

<style>
	/* Card styling */
	.card {
		width: 60px;
		height: 84px;
		border-radius: 4px;
		border: 1px solid #333;
		position: relative;
		display: flex;
		flex-direction: column;
		justify-content: space-between;
		padding: 2px;
		font-size: 0.5rem;
		box-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
		cursor: pointer;
		transition: transform 0.2s ease;
	}

	.card:hover {
		transform: translateY(-1px);
		box-shadow: 1px 2px 4px rgba(0, 0, 0, 0.4);
	}

	.revealed-card {
		background: white;
	}

	.hidden-card {
		background: linear-gradient(135deg, #1e3c72, #2a5298);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.card-back {
		font-size: 2.4rem;
		color: #FFD700;
	}

	.card-top, .card-bottom {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
	}

	.card-bottom {
		transform: rotate(180deg);
	}

	.card-center {
		display: flex;
		align-items: center;
		justify-content: center;
		flex: 1;
	}

	.suit {
		font-size: large;
	}

	.suit-large {
		font-size: 2.4rem;
	}

	.value {
		font-weight: bold;
		font-size: x-large;
	}
</style>