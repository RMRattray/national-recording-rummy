// place files you want to import through the `$lib` alias in this folder.

// Enums for Card attributes
export enum Suit {
    HEARTS = 'hearts',
    DIAMONDS = 'diamonds',
    CLUBS = 'clubs',
    SPADES = 'spades'
}

export enum Rank {
    ACE = 1,
    TWO = 2,
    THREE = 3,
    FOUR = 4,
    FIVE = 5,
    SIX = 6,
    SEVEN = 7,
    EIGHT = 8,
    NINE = 9,
    TEN = 10,
    JACK = 11,
    QUEEN = 12,
    KING = 13,
    HIGH_ACE = 14
}

export enum MeldType {
    NONE = 'NONE',
    SET = 'SET',
    RUN = 'RUN'
}

// Card class
export class Card {
    suit: Suit;
    rank: Rank;
    meld_type: MeldType;

    constructor(suit: Suit, rank: Rank, meld_type: MeldType) {
        this.suit = suit;
        this.rank = rank;
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
    const firstRank = list[0].rank;
    const isSet = list.every(
        card => card.rank === firstRank && card.meld_type !== MeldType.RUN
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

    list.sort((a, b) => a.rank - b.rank);

    // Check consecutive ranks, including Ace–King wrap
    for (let i = 1; i < list.length; i++) {
        const prev = list[i - 1].rank;
        const curr = list[i].rank;

        const normalStep = curr === prev + 1;
        const aceWrap = i === 1 && list[0].rank === 1 && list[0].meld_type === MeldType.NONE && list[list.length - 1].rank === 13;

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
