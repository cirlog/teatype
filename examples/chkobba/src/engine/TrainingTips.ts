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
import { findValidCaptures } from './GameLogic';

// Types
import { isFaceCard, canMakeChkobba, getCardName } from '../types/Card';
import { iGameState } from '../types/GameState';

export interface iTip {
    priority: number; // Higher = more important
    title: string;
    message: string;
    category: 'strategy' | 'warning' | 'opportunity' | 'info';
}

/**
 * Analyze the current game state and provide the best tip
 */
export function getTrainingTip(state: iGameState): iTip | null {
    if (state.currentPlayer !== 'human' || state.human.hand.length === 0) {
        return null;
    }

    const tips: iTip[] = [];
    const hand = state.human.hand;
    const table = state.table;

    // Analyze each card in hand
    for (const card of hand) {
        const captures = findValidCaptures(card, table);

        // Check for Chkobba opportunity (any card except Ace can make Chkobba)
        if (captures.length > 0 && canMakeChkobba(card)) {
            for (const capture of captures) {
                const remainingTable = table.filter(t => !capture.some(c => c.id === t.id));
                if (remainingTable.length === 0) {
                    tips.push({
                        priority: 100,
                        title: '🎯 CHKOBBA POSSIBLE!',
                        message: `Play your ${getCardName(card)} to capture all cards and score a Chkobba point!`,
                        category: 'opportunity',
                    });
                }
            }
        }

        // Check for 7♦ capture opportunity
        if (captures.some(c => c.some(card => card.suit === 'diamonds' && card.rank === 7))) {
            tips.push({
                priority: 95,
                title: '💎 7♦ Sette di Deneri!',
                message: `You can capture the 7♦ - that's a guaranteed point!`,
                category: 'opportunity',
            });
        }

        // Check for capturing multiple 7s
        const capturedSevens = captures.flat().filter(c => c.rank === 7);
        if (capturedSevens.length >= 2) {
            tips.push({
                priority: 85,
                title: '7️⃣ Seven Opportunity',
                message: `You can capture ${capturedSevens.length} sevens at once!`,
                category: 'opportunity',
            });
        }

        // Check for capturing multiple diamonds
        const capturedDiamonds = captures.flat().filter(c => c.suit === 'diamonds');
        if (capturedDiamonds.length >= 3) {
            tips.push({
                priority: 80,
                title: '♦ Diamond Collection',
                message: `Good chance to collect ${capturedDiamonds.length} diamond cards!`,
                category: 'opportunity',
            });
        }
    }

    // Face card strategy tips (J, Q, K are high value cards)
    const faceCards = hand.filter(c => isFaceCard(c));
    const lowCards = hand.filter(c => !isFaceCard(c) && c.rank !== 1);

    if (faceCards.length > 0 && table.length > 0) {
        // Face cards are valuable for high-sum captures
        const faceCaptures = faceCards.some(c => findValidCaptures(c, table).length > 0);
        if (faceCaptures) {
            tips.push({
                priority: 70,
                title: '👑 Face Card Advantage',
                message: 'Your J/Q/K can capture high-value combinations! Use them wisely.',
                category: 'strategy',
            });
        }
    }

    // Check for "easy sum" warning
    for (const card of lowCards) {
        const cardValue = card.value;
        // Check if dropping would create easy capture for opponent
        const newTableSum = table.reduce((s, c) => s + c.value, 0) + cardValue;
        if (newTableSum >= 2 && newTableSum <= 10) {
            const captures = findValidCaptures(card, table);
            if (captures.length === 0) {
                tips.push({
                    priority: 60,
                    title: '⚠️ Careful When Dropping!',
                    message: `Your ${getCardName(card)} would create a table sum of ${newTableSum} - easy for opponent!`,
                    category: 'warning',
                });
            }
        }
    }

    // Ace strategy
    const hasAce = hand.some(c => c.rank === 1);
    if (hasAce) {
        const aceCaptures = findValidCaptures(hand.find(c => c.rank === 1)!, table);
        if (aceCaptures.length > 0 && aceCaptures.some(c => c.length === 1)) {
            tips.push({
                priority: 55,
                title: '🅰️ Ace as Tool',
                message: 'The Ace can snatch single cards - perfect for breaking dangerous table patterns!',
                category: 'info',
            });
        }
    }

    // 7s tracking tip
    const humanSevens = state.human.capturedCards.filter(c => c.rank === 7).length;
    const npcSevens = state.npc.capturedCards.filter(c => c.rank === 7).length;
    const tableSevens = table.filter(c => c.rank === 7).length;

    if (humanSevens < npcSevens && tableSevens > 0) {
        tips.push({
            priority: 75,
            title: '7️⃣ Sevens Chase',
            message: `Opponent leads ${npcSevens}:${humanSevens} in sevens. Try to grab the 7 on the table!`,
            category: 'warning',
        });
    }

    // Diamond majority tracking
    const humanDiamonds = state.human.capturedCards.filter(c => c.suit === 'diamonds').length;
    const npcDiamonds = state.npc.capturedCards.filter(c => c.suit === 'diamonds').length;

    if (npcDiamonds > humanDiamonds + 2) {
        tips.push({
            priority: 65,
            title: '♦ Diamond Deficit',
            message: `Opponent leads ${npcDiamonds}:${humanDiamonds} in diamonds. Prioritize diamond cards!`,
            category: 'warning',
        });
    }

    // Card majority tracking
    const totalCards = state.human.capturedCards.length + state.npc.capturedCards.length;
    if (totalCards > 20) {
        const humanCards = state.human.capturedCards.length;
        const npcCards = state.npc.capturedCards.length;
        if (npcCards > humanCards + 5) {
            tips.push({
                priority: 50,
                title: '📊 Card Majority',
                message: `Opponent has ${npcCards} cards, you only have ${humanCards}. Capture more cards!`,
                category: 'info',
            });
        }
    }

    // No capture available - give dropping advice
    const hasCapture = hand.some(card => findValidCaptures(card, table).length > 0);
    if (!hasCapture && hand.length > 0) {
        // Find best card to drop - prefer low value cards
        const dropPriority = [...hand].sort((a, b) => {
            // Prefer dropping low cards
            let scoreA = a.value;
            let scoreB = b.value;
            // Penalize diamonds
            if (a.suit === 'diamonds') scoreA += 10;
            if (b.suit === 'diamonds') scoreB += 10;
            // Heavily penalize 7s
            if (a.rank === 7) scoreA += 20;
            if (b.rank === 7) scoreB += 20;
            return scoreA - scoreB;
        });

        if (dropPriority.length > 0) {
            const bestDrop = dropPriority[0];
            tips.push({
                priority: 40,
                title: '📤 Drop Card',
                message: `No capture possible. The ${getCardName(bestDrop)} is the safest card to drop.`,
                category: 'info',
            });
        }
    }

    // Sort by priority and return the best tip
    tips.sort((a, b) => b.priority - a.priority);
    return tips[0] || null;
}