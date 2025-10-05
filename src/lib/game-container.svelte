<script lang="ts">
    import { RummyGame, Card, Suit, Value } from '$lib';
    import Playerbox from '$lib/playerbox.svelte';
    import CardBox from '$lib/cardbox.svelte';
    let { 
        currentGame, 
        playerName, 
        socket, 
        drawFromStack, 
        drawFromDiscard, 
        playMeld, 
        discardCard 
    }: { 
        currentGame: RummyGame, 
        playerName: string, 
        socket: any,
        drawFromStack: () => Promise<void>,
        drawFromDiscard: (card: Card) => Promise<void>,
        playMeld: (cards: Card[]) => Promise<void>,
        discardCard: (card: Card) => Promise<void>
    } = $props();
    
    let myPlayerIndex = $derived(currentGame.playerNames.indexOf(playerName));
    let selectedCards = $state<Set<Card>>(new Set());
 
	let leftPlayerIndex = $derived((myPlayerIndex + 1) % currentGame.playerCount);
	let oppoPlayerIndex = $derived(currentGame.playerCount == 2 ? 1 - myPlayerIndex : (myPlayerIndex + 2) % currentGame.playerCount);
	let rightPlayerIndex = $derived((myPlayerIndex + 3) % currentGame.playerCount);

    // Check if it's the current player's turn
    let isMyTurn = $derived(currentGame.activePlayerName === playerName);

    function handleCardClick(card: Card, location: 'discard' | 'stack' | 'hand', event: MouseEvent) {
        if (!isMyTurn) return;

        if (location === 'discard') {
            drawFromDiscard(card);
        } else if (location === 'stack') {
            drawFromStack();
        } else if (location === 'hand') {
            if (event.shiftKey) {
                // Toggle card selection
                const newSelectedCards = new Set(selectedCards);
                if (newSelectedCards.has(card)) {
                    newSelectedCards.delete(card);
                } else {
                    newSelectedCards.add(card);
                }
                selectedCards = newSelectedCards;
            } else {
                // Discard the card
                discardCard(card);
            }
        }
    }

    function handlePlayMeld() {
        if (selectedCards.size > 0) {
            playMeld(Array.from(selectedCards));
            selectedCards = new Set(); // Clear selection after playing
        }
    }

    function isCardSelected(card: Card): boolean {
        return selectedCards.has(card);
    }

	let scrollContainer : HTMLDivElement;

	$effect(() => {
		if (currentGame.eventLog.length > 0) {
			console.log("This line runs");
			scrollContainer.scrollTop = scrollContainer.scrollHeight;
		}
	})

</script>


<div class="game-container">
	<main class="game-main">
        {#if currentGame.playerCount > 2}
        <Playerbox game={currentGame} playerIndex={leftPlayerIndex} vertical={true} lefttop={true} user={false}/> 
        {/if}
        <div class="center-area">
            <Playerbox game={currentGame} playerIndex={oppoPlayerIndex} vertical={false} lefttop={true} user={false}/>
            <!-- Discard pile -->
			<div class="discards-section">
				<h3>Discard Pile</h3>
				<div class="discards">
                    {#if currentGame.stack > 0}
                    <button 
                        class="clickable-card" 
                        class:disabled={!isMyTurn}
                        onclick={(e) => handleCardClick(new Card(Suit.SPADES, Value.ACE), 'stack', e)}
                        type="button"
                        disabled={!isMyTurn}
                    >
                        <CardBox card={new Card(Suit.SPADES, Value.ACE)} revealed={false}/>
                    </button>
                    {/if}
					{#each currentGame.discards as card}
                        <button 
                            class="clickable-card" 
                            class:disabled={!isMyTurn}
                            onclick={(e) => handleCardClick(card, 'discard', e)}
                            type="button"
                            disabled={!isMyTurn}
                        >
                            <CardBox card={card} revealed={true} />
                        </button>
					{/each}
				</div>
			</div>
            <Playerbox 
                game={currentGame} 
                playerIndex={myPlayerIndex} 
                vertical={false} 
                lefttop={false} 
                user={true}
                {handleCardClick}
                {isCardSelected}
                {isMyTurn}
            />
            
            <!-- Play Meld Button -->
            {#if isMyTurn && selectedCards.size > 0}
                <div class="play-meld-section">
                    <button 
                        class="play-meld-button" 
                        onclick={handlePlayMeld}
                        disabled={selectedCards.size === 0}
                        type="button"
                    >
                        Play Meld ({selectedCards.size} cards)
                    </button>
                </div>
            {/if}
        </div>
        {#if currentGame.playerCount > 3}
        <Playerbox game={currentGame} playerIndex={rightPlayerIndex} vertical={true} lefttop={true} user={false}/> 
        {/if}
	</main>

	<!-- Event log positioned alongside game-main -->
	<div class="event-log-section">
		<h3>Events</h3>
		<div bind:this={scrollContainer} class="event-log">
			{#each currentGame.eventLog as event}
				<div class="event-item">{event}</div>
			{/each}
		</div>
	</div>
</div>

<style>
	.game-container {
		height: 100vh;
		display: flex;
		flex-direction: row;
		background: linear-gradient(135deg, #0f4c3a, #1a5f3f);
		color: white;
		font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
		overflow: hidden;
	}

	.game-main {
		flex: 1;
		display: flex;
		gap: 0.5rem;
		padding: 0.5rem;
		overflow: hidden;
		min-height: 0;
	}

	.center-area {
		flex: 2;
		display: flex;
		flex-direction: column;
		gap: 1rem;
		padding: 0.5rem;
		min-width: 0;
	}

	.discards-section {
		background: rgba(0, 0, 0, 0.3);
		border-radius: 6px;
		padding: 0.5rem;
		border: 2px solid #2d7a5f;
		display: flex;
		flex-direction: column;
		align-items: center;
        flex: 2;
	}

	.discards {
		display: flex;
		gap: 0.2rem;
		flex-wrap: wrap;
		justify-content: center;
	}

	.discards-section h3 {
		margin: 0 0 0.5rem 0;
		color: #90EE90;
		text-align: center;
		font-size: 0.9rem;
	}

	/* Event log */
	.event-log-section {
		/* position: fixed; */
		top: 0.5rem;
		right: 0.5rem;
		width: 250px;
		max-height: calc(100vh - 1rem);
		background: rgba(0, 0, 0, 0.9);
		border-radius: 6px;
		padding: 0.5rem;
		border: 1px solid #2d7a5f;
		display: flex;
		flex-direction: column;
		overflow: hidden;
		z-index: 1000;
        margin: 6px;
	}

	.event-log-section h3 {
		margin: 0 0 0.5rem 0;
		color: #90EE90;
		text-align: center;
		font-size: 0.8rem;
	}

	.event-log {
		flex: 1;
		overflow-y: auto;
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.event-item {
		padding: 0.25rem;
		background: rgba(255, 255, 255, 0.1);
		border-radius: 3px;
		font-size: 0.7rem;
		line-height: 1.2;
		border-left: 2px solid #90EE90;
	}

	/* Scrollbar styling */
	.event-log::-webkit-scrollbar {
		width: 4px;
	}

	.event-log::-webkit-scrollbar-track {
		background: rgba(0, 0, 0, 0.2);
		border-radius: 2px;
	}

	.event-log::-webkit-scrollbar-thumb {
		background: #90EE90;
		border-radius: 2px;
	}

	.event-log::-webkit-scrollbar-thumb:hover {
		background: #7FCF7F;
	}

	/* Clickable card styles */
	.clickable-card {
		cursor: pointer;
		transition: transform 0.2s ease;
	}

	.clickable-card:hover:not(.disabled) {
		transform: translateY(-2px);
	}

	.clickable-card.disabled {
		cursor: not-allowed;
		opacity: 0.5;
	}

	/* Play meld button styles */
	.play-meld-section {
		display: flex;
		justify-content: center;
		margin-top: 1rem;
	}

	.play-meld-button {
		background: linear-gradient(135deg, #2d7a5f, #1e5f3f);
		color: white;
		border: none;
		padding: 0.75rem 1.5rem;
		border-radius: 6px;
		font-size: 0.9rem;
		font-weight: bold;
		cursor: pointer;
		transition: all 0.3s ease;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
	}

	.play-meld-button:hover:not(:disabled) {
		background: linear-gradient(135deg, #3a8b6f, #2d7a5f);
		transform: translateY(-1px);
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
	}

	.play-meld-button:disabled {
		background: #666;
		cursor: not-allowed;
		opacity: 0.6;
	}

	/* Responsive adjustments for very small screens */
	@media (max-height: 500px) {
		
		.event-log-section {
			width: 150px;
		}
	}

</style>