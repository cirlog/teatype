/**
 * @license
 * Copyright (C) 2024-2026 Burak Günaydin
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 */

/**
 * Card types and game constants for Chkobba (French variant)
 * 
 * Deck: 40 cards (French deck with J, Q, K instead of 8, 9, 10)
 * Values: Ace = 1, 2-7 = face value, J=8, Q=9, K=10
 * All cards can capture by matching sums - no special "picture card" rules
 */
type tSuit = 'hearts' | 'diamonds' | 'clubs' | 'spades';
type tRank = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 'J' | 'Q' | 'K';

interface iCard {
    id: string;
    suit: tSuit;
    rank: tRank;
    value: number; // For gameplay calculations
}

const SUITS: tSuit[] = ['hearts', 'diamonds', 'clubs', 'spades'];
const RANKS: tRank[] = [1, 2, 3, 4, 5, 6, 7, 'J', 'Q', 'K'];

// Face cards (J, Q, K) - in French Chkobba these are just higher value cards
const FACE_CARDS: tRank[] = ['J', 'Q', 'K'];

// Rank values for gameplay calculations
const RANK_VALUES: Record<tRank, number> = {
    1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 'J': 8, 'Q': 9, 'K': 10
};

// Cards that can make Chkobba (2-7 and face cards, not Ace)
const CHKOBBA_ELIGIBLE_RANKS: tRank[] = [2, 3, 4, 5, 6, 7, 'J', 'Q', 'K'];

/**
 * Create a unique card ID
 */
const createCardId = (suit: tSuit, rank: tRank): string => {
    return `${suit}-${rank}`;
}

/**
 * Create a single card
 */
const createCard = (suit: tSuit, rank: tRank): iCard => {
    return {
        id: createCardId(suit, rank),
        suit,
        rank,
        value: RANK_VALUES[rank], // Use mapped value (J=8, Q=9, K=10)
    };
}

/**
 * Create a full 40-card deck
 */
const createDeck = (): iCard[] => {
    const deck: iCard[] = [];
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
const shuffleDeck = (deck: iCard[]): iCard[] => {
    const shuffled = [...deck];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

/**
 * Check if a card is a face card (J, Q, K)
 * In French Chkobba, these are regular cards with higher values
 */
const isFaceCard = (card: iCard): boolean => {
    return FACE_CARDS.includes(card.rank);
}

/**
 * Check if a card can make a Chkobba (2-7 only, not Ace)
 */
const canMakeChkobba = (card: iCard): boolean => {
    return CHKOBBA_ELIGIBLE_RANKS.includes(card.rank);
}

/**
 * Get card display name
 */
const getCardName = (card: iCard): string => {
    const rankNames: Record<tRank, string> = {
        1: 'A',
        2: '2',
        3: '3',
        4: '4',
        5: '5',
        6: '6',
        7: '7',
        'J': 'J',
        'Q': 'Q',
        'K': 'K',
    };

    const suitSymbols: Record<tSuit, string> = {
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
const getSuitColor = (suit: tSuit): 'red' | 'black' => {
    return suit === 'hearts' || suit === 'diamonds' ? 'red' : 'black';
}

export {
    SUITS,
    RANKS,

    createDeck,
    shuffleDeck,
    isFaceCard,
    canMakeChkobba,
    getCardName,
    getSuitColor
};

export type {
    iCard,
    tSuit,
    tRank
};
