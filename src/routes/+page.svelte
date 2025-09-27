<script lang="ts">
	import { Card, RummyGame, Suit, Value } from '$lib';
    import CardBox from '$lib/cardbox.svelte';

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
			[[new Card(Suit.HEARTS, Value.KING), new Card(Suit.DIAMONDS, Value.KING), new Card(Suit.CLUBS, Value.KING)],[new Card(Suit.SPADES, Value.ACE), new Card(Suit.SPADES, Value.TWO), new Card(Suit.SPADES, Value.THREE)]]
			[[new Card(Suit.SPADES, Value.ACE), new Card(Suit.SPADES, Value.TWO), new Card(Suit.SPADES, Value.THREE)]],
			[[new Card(Suit.CLUBS, Value.JACK), new Card(Suit.CLUBS, Value.QUEEN), new Card(Suit.CLUBS, Value.KING)]],[]
		],
		[
			new Card(Suit.SPADES, Value.JACK),
			new Card(Suit.HEARTS, Value.QUEEN),
			new Card(Suit.CLUBS, Value.KING)
		],
		20, // stack
		'Bob', // active player
		3,
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
	$: otherPlayers = sampleGame.playerNames.filter(name => name !== playerName);

	
</script>

<div class="game-container">
	<header>
		<h1>National Recording Rummy</h1>
		<div class="game-info">
			<span>Game ID: {sampleGame.gameID}</span>
			<span>Stack: {sampleGame.stack}</span>
			<span>Player: {playerName}</span>
		</div>
	</header>

	<main class="game-main">
		<!-- Left player -->
		<div class="player-left" class:active={otherPlayers.length > 0 && otherPlayers[0] === sampleGame.activePlayerName}>
			<div class="player-info">
				<span class="player-name">{otherPlayers.length > 0 ? otherPlayers[0] : 'Player 1'}</span>
				<span class="card-count">({otherPlayers.length > 0 ? sampleGame.handCts[sampleGame.playerNames.indexOf(otherPlayers[0])] : 0} cards)</span>
			</div>
			<div class="player-area vertical">
				<!-- Melds -->
				<div class="melds">
					{#if otherPlayers.length > 0}
						{#each sampleGame.melds[sampleGame.playerNames.indexOf(otherPlayers[0])] as meld}
                        {#each meld as card}
							<CardBox card={card} revealed={true} />
							{/each}
						{/each}
					{/if}
				</div>
				<!-- Hand -->
				<div class="player-hand">
					{#if otherPlayers.length > 0}
						{#each Array(sampleGame.handCts[sampleGame.playerNames.indexOf(otherPlayers[0])]) as _, i}
							<CardBox card={new Card(Suit.SPADES, Value.ACE)} revealed={false} />
						{/each}
					{/if}
				</div>
			</div>
		</div>

		<!-- Center area with discard pile and current player -->
		<div class="center-area">
			<!-- Discard pile -->
			<div class="discards-section">
				<h3>Discard Pile</h3>
				<div class="discards">
					{#each sampleGame.discards as card}
						<CardBox card={card} revealed={true} />
						
					{/each}
				</div>
			</div>

			<!-- Current player's hand -->
			<div class="your-hand-section" class:active={playerName === sampleGame.activePlayerName}>
				<div class="player-info">
					<span class="player-name">{playerName} (You)</span>
					<span class="card-count">({sampleGame.hand.length} cards)</span>
				</div>
				<div class="your-hand">
					{#each sampleGame.hand as card}
						    <CardBox card={card} revealed={true} />
							
					{/each}
				</div>
			</div>
		</div>

		<!-- Right player -->
		<div class="player-right" class:active={otherPlayers.length > 1 && otherPlayers[1] === sampleGame.activePlayerName}>
			<div class="player-info">
				<span class="player-name">{otherPlayers.length > 1 ? otherPlayers[1] : 'Player 2'}</span>
				<span class="card-count">({otherPlayers.length > 1 ? sampleGame.handCts[sampleGame.playerNames.indexOf(otherPlayers[1])] : 0} cards)</span>
			</div>
			<div class="player-area vertical">
				<!-- Melds -->
				<div class="melds">
					{#if otherPlayers.length > 1}
						    {#each sampleGame.melds[sampleGame.playerNames.indexOf(otherPlayers[1])] as meld}
							{#each meld as card}
							<CardBox card={card} revealed={true} />
							{/each}
						{/each}
					{/if}
				</div>
				<!-- Hand -->
				<div class="player-hand">
					{#if otherPlayers.length > 1}
						{#each Array(sampleGame.handCts[sampleGame.playerNames.indexOf(otherPlayers[1])]) as _, i}
							<CardBox card={new Card(Suit.SPADES, Value.ACE)} revealed={false} />
						{/each}
					{/if}
				</div>
			</div>
		</div>
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
		flex-direction: column;
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

	/* Player positioning */
	.player-left {
		flex: 1;
		background: rgba(0, 0, 0, 0.3);
		border-radius: 6px;
		padding: 0.5rem;
		border: 2px solid transparent;
		transition: all 0.3s ease;
		min-width: 150px;
		max-width: 200px;
		display: flex;
		flex-direction: column;
	}

	.player-right {
		flex: 1;
		background: rgba(0, 0, 0, 0.3);
		border-radius: 6px;
		padding: 0.5rem;
		border: 2px solid transparent;
		transition: all 0.3s ease;
		min-width: 150px;
		max-width: 200px;
		display: flex;
		flex-direction: column;
	}

	.center-area {
		flex: 2;
		display: flex;
		flex-direction: column;
		gap: 1rem;
		padding: 0.5rem;
		min-width: 0;
	}

	.discards-section, .your-hand-section {
		background: rgba(0, 0, 0, 0.3);
		border-radius: 6px;
		padding: 0.5rem;
		border: 2px solid #2d7a5f;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.your-hand-section {
		flex: 1;
		border: 2px solid transparent;
		transition: all 0.3s ease;
	}

	.your-hand-section.active {
		border-color: #FFD700;
		background: rgba(255, 215, 0, 0.1);
		box-shadow: 0 0 8px rgba(255, 215, 0, 0.3);
	}

	/* Active player highlighting */
	.player-left.active,
	.player-right.active {
		border-color: #FFD700;
		background: rgba(255, 215, 0, 0.1);
		box-shadow: 0 0 8px rgba(255, 215, 0, 0.3);
	}

	/* Player info */
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

	/* Player areas */
	.player-area {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.player-area.vertical {
		align-items: center;
	}

	/* Melds and hands */
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

	.discards, .your-hand {
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




	/* Section headers */
	.player-info {
		margin: 0 0 0.5rem 0;
		color: #90EE90;
		text-align: center;
		font-size: 0.9rem;
	}

	/* Event log */
	.event-log-section {
		position: fixed;
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
		.card {
			width: 30px;
			height: 42px;
			font-size: 0.4rem;
		}
		
		.suit-large {
			font-size: 0.6rem;
		}
		
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

	/* Adjust for different player counts */
	@media (max-width: 800px) {
		.player-left,
		.player-right {
			min-width: 100px;
			max-width: 110px;
		}
	}
</style>
