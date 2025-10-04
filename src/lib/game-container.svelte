<script lang="ts">
    import { RummyGame, Card, Suit, Value } from '$lib';
    import Playerbox from '$lib/playerbox.svelte';
    import CardBox from '$lib/cardbox.svelte';
    let { currentGame, playerName, socket }: { currentGame: RummyGame, playerName: string, socket: any } = $props();
    let myPlayerIndex = $derived(currentGame.playerNames.indexOf(playerName));
 
	let leftPlayerIndex = $derived((myPlayerIndex + 1) % currentGame.playerCount);
	let oppoPlayerIndex = $derived(currentGame.playerCount == 2 ? 1 - myPlayerIndex : (myPlayerIndex + 2) % currentGame.playerCount);
	let rightPlayerIndex = $derived((myPlayerIndex + 3) % currentGame.playerCount);

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
                    <CardBox card={new Card(Suit.SPADES, Value.ACE)} revealed={false}/>
                    {/if}
					{#each currentGame.discards as card}
						<CardBox card={card} revealed={true} />
					{/each}
				</div>
			</div>
            <Playerbox game={currentGame} playerIndex={myPlayerIndex} vertical={false} lefttop={false} user={true}/>
        </div>
        {#if currentGame.playerCount > 3}
        <Playerbox game={currentGame} playerIndex={rightPlayerIndex} vertical={true} lefttop={true} user={false}/> 
        {/if}
	</main>

	<!-- Event log positioned alongside game-main -->
	<div class="event-log-section">
		<h3>Events</h3>
		<div class="event-log">
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

	/* Responsive adjustments for very small screens */
	@media (max-height: 500px) {
		
		.event-log-section {
			width: 150px;
		}
	}

</style>