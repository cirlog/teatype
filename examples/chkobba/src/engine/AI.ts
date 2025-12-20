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

// Components
import { findValidCaptures, executeCapture, executeDrop } from './GameLogic';

// Types
import { iCard, isFaceCard, canMakeChkobba } from '../types/Card';
import { iGameState, tDifficulty } from '../types/GameState';

interface iMove {
    card: iCard;
    capture: iCard[] | null;
    score: number;
}

export function executeNPCTurn(state: iGameState): iGameState {
    // Safety check - if NPC has no cards, return unchanged state
    if (state.npc.hand.length === 0) {
        console.warn('NPC has no cards to play');
        return state;
    }

    const move = selectMove(state);

    // Safety check - if no valid move found
    if (!move || !move.card) {
        console.warn('No valid move found for NPC');
        return state;
    }

    if (move.capture && move.capture.length > 0) {
        return executeCapture(state, 'npc', move.card, move.capture);
    }
    return executeDrop(state, 'npc', move.card);
}

/**
 * Select the best move based on difficulty
 */
function selectMove(state: iGameState): iMove {
    const { difficulty } = state;
    const hand = state.npc.hand;
    const table = state.table;

    // Generate all possible moves
    const moves: iMove[] = hand.map(card => {
        const captures = findValidCaptures(card, table);

        if (captures.length > 0) {
            // Has captures available
            const bestCapture = selectBestCapture(card, captures, state, difficulty);
            return { card, capture: bestCapture, score: 0 };
        }

        // No capture possible
        return { card, capture: null, score: 0 };
    });

    // Score each move based on difficulty
    const scoredMoves = moves.map(move => ({
        ...move,
        score: evaluateMove(move, state, difficulty),
    }));

    // Select move based on difficulty
    switch (difficulty) {
        case 'easy':
            return selectEasyMove(scoredMoves);
        case 'medium':
            return selectMediumMove(scoredMoves);
        case 'hard':
            return selectHardMove(scoredMoves);
        case 'expert':
            return selectExpertMove(scoredMoves, state);
        default:
            return selectMediumMove(scoredMoves);
    }
}

/**
 * Select best capture from multiple options
 */
function selectBestCapture(
    _card: iCard,
    captures: iCard[][],
    state: iGameState,
    difficulty: tDifficulty
): iCard[] {
    if (captures.length === 1) return captures[0];

    // Score each capture option
    const scoredCaptures = captures.map(capture => ({
        capture,
        score: evaluateCaptureValue(capture, state, difficulty),
    }));

    // Sort by score descending
    scoredCaptures.sort((a, b) => b.score - a.score);

    // Add randomness for easier difficulties
    if (difficulty === 'easy') {
        return captures[Math.floor(Math.random() * captures.length)];
    }
    if (difficulty === 'medium' && Math.random() < 0.3) {
        return captures[Math.floor(Math.random() * captures.length)];
    }

    return scoredCaptures[0].capture;
}

/**
 * Evaluate the value of a capture
 */
function evaluateCaptureValue(capture: iCard[], state: iGameState, difficulty: tDifficulty): number {
    let score = capture.length * 10; // Base score for number of cards

    for (const card of capture) {
        // Diamonds are valuable
        if (card.suit === 'diamonds') {
            score += 15;
            // 7♦ is especially valuable
            if (card.rank === 7) {
                score += 50;
            }
        }

        // Sevens are valuable
        if (card.rank === 7) {
            score += 20;
        }

        // Higher difficulty considers opponent's captured cards
        if (difficulty === 'hard' || difficulty === 'expert') {
            const humanDiamonds = state.human.capturedCards.filter(c => c.suit === 'diamonds').length;
            const npcDiamonds = state.npc.capturedCards.filter(c => c.suit === 'diamonds').length;

            // Prioritize diamonds if behind
            if (card.suit === 'diamonds' && npcDiamonds <= humanDiamonds) {
                score += 25;
            }
        }
    }

    return score;
}

/**
 * Evaluate a complete move
 */
function evaluateMove(move: iMove, state: iGameState, difficulty: tDifficulty): number {
    let score = 0;

    // Capturing is always preferred
    if (move.capture && move.capture.length > 0) {
        score += 100 + evaluateCaptureValue(move.capture, state, difficulty);

        // Check for Chkobba potential
        const remainingTable = state.table.filter(
            c => !move.capture!.some(cc => cc.id === c.id)
        );
        if (remainingTable.length === 0 && canMakeChkobba(move.card)) {
            score += 200; // Chkobba is very valuable
        }
    } else {
        // Evaluate the drop
        score += evaluateDrop(move.card, state, difficulty);
    }

    return score;
}

/**
 * Evaluate dropping a card (when no capture possible)
 */
function evaluateDrop(card: iCard, state: iGameState, difficulty: tDifficulty): number {
    let score = 0;

    // Face cards (J, Q, K) are high value - prefer not to drop
    if (isFaceCard(card)) {
        score -= 15;
    }

    // Don't drop valuable cards if possible
    if (card.suit === 'diamonds') {
        score -= 20;
        if (card.rank === 7) {
            score -= 100; // Never drop 7♦ if avoidable
        }
    }

    if (card.rank === 7) {
        score -= 30;
    }

    // Higher difficulties consider what opponent could capture
    if (difficulty === 'hard' || difficulty === 'expert') {
        const newTableSum = state.table.reduce((sum, c) => sum + c.value, 0) + card.value;

        // If dropping creates easy capture opportunity for opponent
        for (let possibleCard = 2; possibleCard <= 10; possibleCard++) {
            if (newTableSum === possibleCard) {
                score -= 50; // Opponent could clear with a single card
            }
        }
    }

    // Prefer dropping low-value cards (face cards are high value: J=8, Q=9, K=10)
    score += (11 - card.value) * 5;

    return score;
}

/**
 * Easy: Mostly random with slight preference for captures
 */
function selectEasyMove(moves: iMove[]): iMove {
    // 70% chance to just pick randomly
    if (Math.random() < 0.7) {
        return moves[Math.floor(Math.random() * moves.length)];
    }

    // Otherwise, prefer any capture
    const captureMoves = moves.filter(m => m.capture && m.capture.length > 0);
    if (captureMoves.length > 0) {
        return captureMoves[Math.floor(Math.random() * captureMoves.length)];
    }

    return moves[Math.floor(Math.random() * moves.length)];
}

/**
 * Medium: Basic strategy with some randomness
 */
function selectMediumMove(moves: iMove[]): iMove {
    // Sort by score
    const sorted = [...moves].sort((a, b) => b.score - a.score);

    // 20% chance to not pick optimal
    if (Math.random() < 0.2 && sorted.length > 1) {
        return sorted[1];
    }

    return sorted[0];
}

/**
 * Hard: Strong strategy, minimal mistakes
 */
function selectHardMove(moves: iMove[]): iMove {
    const sorted = [...moves].sort((a, b) => b.score - a.score);

    // 5% chance for suboptimal play
    if (Math.random() < 0.05 && sorted.length > 1) {
        return sorted[1];
    }

    return sorted[0];
}

/**
 * Expert: Optimal play with card counting and lookahead
 */
function selectExpertMove(moves: iMove[], state: iGameState): iMove {
    // Advanced evaluation considering remaining cards
    const enhancedMoves = moves.map(move => {
        let enhancedScore = move.score;

        // Card counting - know what's been played
        const playedCards = [
            ...state.human.capturedCards,
            ...state.npc.capturedCards,
            ...state.table,
        ];

        // Calculate remaining sevens and diamonds for future use
        const _remainingSevens = 4 - playedCards.filter(c => c.rank === 7).length;
        const _remainingDiamonds = 10 - playedCards.filter(c => c.suit === 'diamonds').length;

        // Adjust strategy based on remaining cards
        if (move.capture) {
            const capturedSevens = move.capture.filter(c => c.rank === 7).length;
            const capturedDiamonds = move.capture.filter(c => c.suit === 'diamonds').length;

            // Prioritize if close to majority
            if (capturedSevens > 0 && state.npc.capturedCards.filter(c => c.rank === 7).length + capturedSevens >= 3) {
                enhancedScore += 100; // Could get sevens majority
            }
            if (capturedDiamonds > 0) {
                const npcDiamonds = state.npc.capturedCards.filter(c => c.suit === 'diamonds').length;
                if (npcDiamonds + capturedDiamonds > 5) {
                    enhancedScore += 80; // Could get diamonds majority
                }
            }
        }

        // Consider endgame scenarios
        const cardsRemaining = state.deck.length + state.human.hand.length + state.npc.hand.length;
        if (cardsRemaining <= 6) {
            // Endgame - maximize final capture opportunity
            if (!move.capture && state.table.length > 3) {
                enhancedScore -= 50; // Don't add to large table at endgame
            }
        }

        return { ...move, score: enhancedScore };
    });

    enhancedMoves.sort((a, b) => b.score - a.score);
    return enhancedMoves[0];
}

/**
 * Add thinking delay for more natural gameplay
 */
export function getNPCThinkingTime(difficulty: tDifficulty): number {
    switch (difficulty) {
        case 'easy':
            return 500 + Math.random() * 500;
        case 'medium':
            return 800 + Math.random() * 700;
        case 'hard':
            return 1000 + Math.random() * 1000;
        case 'expert':
            return 1500 + Math.random() * 1000;
        default:
            return 1000;
    }
}
