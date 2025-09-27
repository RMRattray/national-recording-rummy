<script lang="ts">
	import { Card, RummyGame, Suit, Value } from '$lib';
    import CardBox from '$lib/cardbox.svelte';
    import Playerbox from '$lib/playerbox.svelte';

	// Current player state
	let playerName = 'Alice'; // Current user

	// Sample game data
	const sampleGame = new RummyGame(
		'game123',
		['Alice', 'Bob', 'Charlie', 'Diana'], // 4 players including user
		[
			new Card(Suit.HEARTS, Value.ACE),
			new Card(Suit.DIAMONDS, Value.TWO),
			new Card(Suit.CLUBS, Value.THREE),
			new Card(Suit.SPADES, Value.FOUR),
			new Card(Suit.HEARTS, Value.FIVE),
			new Card(Suit.DIAMONDS, Value.SIX),
			new Card(Suit.CLUBS, Value.SEVEN)
		],
		[7, 7, 7, 7], // hand counts for each player
		[
			[
                [new Card(Suit.HEARTS, Value.KING), new Card(Suit.DIAMONDS, Value.KING), new Card(Suit.CLUBS, Value.KING)],
                [new Card(Suit.SPADES, Value.ACE), new Card(Suit.SPADES, Value.TWO), new Card(Suit.SPADES, Value.THREE)]
            ],
			[
                [new Card(Suit.SPADES, Value.ACE), new Card(Suit.SPADES, Value.TWO), new Card(Suit.SPADES, Value.THREE)]
            ],
			[
                [new Card(Suit.CLUBS, Value.JACK), new Card(Suit.CLUBS, Value.QUEEN), new Card(Suit.CLUBS, Value.KING)]
            ],
            [
                [new Card(Suit.DIAMONDS, Value.JACK), new Card(Suit.DIAMONDS, Value.QUEEN), new Card(Suit.DIAMONDS, Value.KING)]
            ]
		],
		[
			new Card(Suit.SPADES, Value.JACK),
			new Card(Suit.HEARTS, Value.QUEEN),
			new Card(Suit.CLUBS, Value.KING)
		],
		20, // stack
		'Bob', // active player
		4,
		[
			'Game started',
			'Alice drew a card',
			'Alice played a set of Kings',
			'Bob drew from discard pile',
			'Bob played a run of Spades',
			'Charlie drew from deck',
			'Charlie played a run of Clubs'
		]
	);

	// Get other players (excluding current user)
    $: myPlayerIndex = sampleGame.playerNames.indexOf(playerName);

</script>

<div class="game-container">

	<main class="game-main">
        {#if sampleGame.playerCount > 2}
        <Playerbox game={sampleGame} playerIndex={(myPlayerIndex + 1) % sampleGame.playerCount} vertical={true} lefttop={true} user={false}/> 
        {/if}
        <div class="center-area">
            <Playerbox game={sampleGame} playerIndex={sampleGame.playerCount == 2 ? 1 - myPlayerIndex : (myPlayerIndex + 2) % sampleGame.playerCount} vertical={false} lefttop={true} user={false}/>
            <!-- Discard pile -->
			<div class="discards-section">
				<h3>Discard Pile</h3>
				<div class="discards">
                    {#if sampleGame.stack > 0}
                    <CardBox card={new Card(Suit.SPADES, Value.ACE)} revealed={false}/>
                    {/if}
					{#each sampleGame.discards as card}
						<CardBox card={card} revealed={true} />
						
					{/each}
				</div>
			</div>
            <Playerbox game={sampleGame} playerIndex={myPlayerIndex} vertical={false} lefttop={false} user={true}/>
        </div>
        {#if sampleGame.playerCount > 3}
        <Playerbox game={sampleGame} playerIndex={(myPlayerIndex + 3) % sampleGame.playerCount} vertical={true} lefttop={true} user={false}/> 
        {/if}
	</main>

	<!-- Event log positioned alongside game-main -->
	<div class="event-log-section">
		<h3>Events</h3>
		<div class="event-log">
			{#each sampleGame.eventLog as event}
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

	header {
		padding: 0.5rem 1rem;
		background: rgba(0, 0, 0, 0.2);
		border-bottom: 1px solid #2d7a5f;
		flex-shrink: 0;
	}

	header h1 {
		margin: 0 0 0.25rem 0;
		font-size: 1.5rem;
		text-align: center;
		color: #90EE90;
	}

	.game-info {
		display: flex;
		justify-content: center;
		gap: 1rem;
		font-size: 0.8rem;
		opacity: 0.8;
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
		
		header h1 {
			font-size: 1.2rem;
		}
		
		.game-info {
			font-size: 0.7rem;
		}
	}

</style>
