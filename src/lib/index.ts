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

export enum MeldType {
    NONE = 'NONE',
    SET = 'SET',
    RUN = 'RUN'
}

// Card class
export class Card {
    suit: Suit;
    value: Value;
    meld_type: MeldType;

    constructor(suit: Suit, value: Value, meld_type: MeldType) {
        this.suit = suit;
        this.value = value;
        this.meld_type = meld_type;
    }
}

// Function to see if a meld is formed
export function formsMeld(cards: Set<Card>): boolean {
    const list = Array.from(cards);

    if (list.length < 3) {
        return false;
    }

    // ----- Check for SET -----
    const firstRank = list[0].value;
    const isSet = list.every(
        card => card.value === firstRank && card.meld_type !== MeldType.RUN
    );

    if (isSet) {
        return true;
    }

    // ----- Check for RUN -----
    const firstSuit = list[0].suit;
    const sameSuit = list.every(
        card => card.suit === firstSuit && card.meld_type !== MeldType.SET
    );

    if (!sameSuit) {
        return false;
    }

    // Sort ranks
    const valueMenu = new Map<Value, number>();
    valueMenu.set(Value.ACE, 1);
    valueMenu.set(Value.TWO, 2);
    valueMenu.set(Value.THREE, 3);
    valueMenu.set(Value.FOUR, 4);
    valueMenu.set(Value.FIVE, 5);
    valueMenu.set(Value.SIX, 6);
    valueMenu.set(Value.SEVEN, 7);
    valueMenu.set(Value.EIGHT, 8);
    valueMenu.set(Value.NINE, 9);
    valueMenu.set(Value.TEN, 10);
    valueMenu.set(Value.JACK, 11);
    valueMenu.set(Value.QUEEN, 12);
    valueMenu.set(Value.KING, 13);

    const ranks = list
        .map(card => card.value)
        .map(x => valueMenu.get(x)!)
        .sort((a, b) => a - b);

    // Check consecutive ranks, including Ace–King wrap
    for (let i = 1; i < ranks.length; i++) {
        const prev = ranks[i - 1];
        const curr = ranks[i];

        const normalStep = curr === prev + 1;
        const aceWrap = i === 1 && ranks[0] === 1 && ranks[ranks.length - 1] === 13;

        if (!normalStep && !aceWrap) {
            return false;
        }
    }

    return true;
}

// RummyGame class
export class RummyGame {
    gameID: string;
    playerNames: string[];
    playerScores: number[];
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
        playerScores: number[],
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
        this.playerScores = playerScores;
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
