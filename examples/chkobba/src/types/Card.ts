/**
 * Card types and game constants for Tunisian Chkobba
 * 
 * Deck: 40 cards (French deck WITH 8, 9, 10 - without J, Q, K)
 * Values: Ace = 1, 2-7 = face value, 8/9/10 = special picture cards
 */

export type Suit = 'hearts' | 'diamonds' | 'clubs' | 'spades';
export type Rank = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;

export interface Card {
    id: string;
    suit: Suit;
    rank: Rank;
    value: number; // For gameplay calculations
}

export const SUITS: Suit[] = ['hearts', 'diamonds', 'clubs', 'spades'];
export const RANKS: Rank[] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

// Picture cards (8, 9, 10) - these take ALL cards from the table
export const PICTURE_CARDS: Rank[] = [8, 9, 10];

// Number cards that can make Chkobba (not Ace, not picture cards)
export const CHKOBBA_ELIGIBLE_RANKS: Rank[] = [2, 3, 4, 5, 6, 7];

/**
 * Create a unique card ID
 */
export function createCardId(suit: Suit, rank: Rank): string {
    return `${suit}-${rank}`;
}

/**
 * Create a single card
 */
export function createCard(suit: Suit, rank: Rank): Card {
    return {
        id: createCardId(suit, rank),
        suit,
        rank,
        value: rank, // In Tunisian Chkobba, card value equals rank
    };
}

/**
 * Create a full 40-card deck
 */
export function createDeck(): Card[] {
    const deck: Card[] = [];
    for (const suit of SUITS) {
        for (const rank of RANKS) {
            deck.push(createCard(suit, rank));
        }
    }
    return deck;
}

/**
 * Fisher-Yates shuffle algorithm
 */
export function shuffleDeck(deck: Card[]): Card[] {
    const shuffled = [...deck];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

/**
 * Check if a card is a picture card (8, 9, 10)
 */
export function isPictureCard(card: Card): boolean {
    return PICTURE_CARDS.includes(card.rank);
}

/**
 * Check if a card can make a Chkobba (2-7 only, not Ace)
 */
export function canMakeChkobba(card: Card): boolean {
    return CHKOBBA_ELIGIBLE_RANKS.includes(card.rank);
}

/**
 * Get card display name
 */
export function getCardName(card: Card): string {
    const rankNames: Record<Rank, string> = {
        1: 'A',
        2: '2',
        3: '3',
        4: '4',
        5: '5',
        6: '6',
        7: '7',
        8: '8',
        9: '9',
        10: '10',
    };

    const suitSymbols: Record<Suit, string> = {
        hearts: '♥',
        diamonds: '♦',
        clubs: '♣',
        spades: '♠',
    };

    return `${rankNames[card.rank]}${suitSymbols[card.suit]}`;
}

/**
 * Get suit color
 */
export function getSuitColor(suit: Suit): 'red' | 'black' {
    return suit === 'hearts' || suit === 'diamonds' ? 'red' : 'black';
}
