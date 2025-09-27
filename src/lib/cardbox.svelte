<script lang="ts">
	import { Card, Suit } from '$lib';
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
</script>

<div class="card" class:revealed-card={revealed} class:hidden-card={!revealed}>
    {#if revealed}
        <div class="card-top" style="color: {getCardColor(card.suit)}">
            <span class="suit">{getSuitSymbol(card.suit)}</span>
            <span class="value">{card.value}</span>
        </div>
        <div class="card-center" style="color: {getCardColor(card.suit)}">
            <span class="suit-large">{getSuitSymbol(card.suit)}</span>
        </div>
        <div class="card-bottom" style="color: {getCardColor(card.suit)}">
            <span class="suit">{getSuitSymbol(card.suit)}</span>
            <span class="value">{card.value}</span>
        </div>
    {:else}
        <div class="card-back">🂠</div>
    {/if}
</div>

<style>
	/* Card styling */
	.card {
		width: 35px;
		height: 49px;
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
		font-size: 1rem;
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

	.suit-large {
		font-size: 0.8rem;
	}

	.value {
		font-weight: bold;
	}
</style>