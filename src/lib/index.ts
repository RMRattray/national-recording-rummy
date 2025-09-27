// place files you want to import through the `$lib` alias in this folder.

// Enums for Card attributes
export enum Suit {
    HEARTS = 'hearts',
    DIAMONDS = 'diamonds',
    CLUBS = 'clubs',
    SPADES = 'spades'
}

export enum Value {
    ACE = 'A',
    TWO = '2',
    THREE = '3',
    FOUR = '4',
    FIVE = '5',
    SIX = '6',
    SEVEN = '7',
    EIGHT = '8',
    NINE = '9',
    TEN = '10',
    JACK = 'J',
    QUEEN = 'Q',
    KING = 'K'
}

// Card class
export class Card {
    suit: Suit;
    value: Value;

    constructor(suit: Suit, value: Value) {
        this.suit = suit;
        this.value = value;
    }
}

// RummyGame class
export class RummyGame {
    gameID: string;
    playerNames: string[];
    hand: Card[];
    handCts: number[];
    melds: Card[][][]; // by player, then by meld, then by 
    discards: Card[];
    stack: number;
    activePlayerName: string;
    playerCount: number;
    eventLog: string[];

    constructor(
        gameID: string,
        playerNames: string[],
        hand: Card[],
        handCts: number[],
        melds: Card[][][],
        discards: Card[],
        stack: number,
        activePlayerName: string,
        playerCount: number,
        eventLog: string[]
    ) {
        this.gameID = gameID;
        this.playerNames = playerNames;
        this.hand = hand;
        this.handCts = handCts;
        this.melds = melds;
        this.discards = discards;
        this.stack = stack;
        this.activePlayerName = activePlayerName;
        this.playerCount = playerCount;
        this.eventLog = eventLog;
    }
}
