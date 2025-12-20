/**
 * Training tips and strategy guide for Tunisian Chkobba
 * Based on expert strategies to improve gameplay
 */

import { isPictureCard } from '../types/Card';
import { GameState } from '../types/GameState';
import { findValidCaptures } from './GameLogic';

export interface Tip {
    priority: number; // Higher = more important
    title: string;
    message: string;
    category: 'strategy' | 'warning' | 'opportunity' | 'info';
}

/**
 * Analyze the current game state and provide the best tip
 */
export function getTrainingTip(state: GameState): Tip | null {
    if (state.currentPlayer !== 'human' || state.human.hand.length === 0) {
        return null;
    }

    const tips: Tip[] = [];
    const hand = state.human.hand;
    const table = state.table;

    // Analyze each card in hand
    for (const card of hand) {
        const captures = findValidCaptures(card, table);

        // Check for Chkobba opportunity
        if (captures.length > 0 && !isPictureCard(card) && card.rank >= 2 && card.rank <= 7) {
            for (const capture of captures) {
                const remainingTable = table.filter(t => !capture.some(c => c.id === t.id));
                if (remainingTable.length === 0) {
                    tips.push({
                        priority: 100,
                        title: '🎯 CHKOBBA POSSIBLE!',
                        message: `Play your ${card.rank} to capture all cards and score a Chkobba point!`,
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

    // Picture card strategy tips
    const pictureCards = hand.filter(c => isPictureCard(c));
    const normalCards = hand.filter(c => !isPictureCard(c));

    if (pictureCards.length > 0 && table.length > 0) {
        // Warn against playing picture cards too early
        if (normalCards.length > 0 && table.length < 4) {
            tips.push({
                priority: 70,
                title: '⚠️ Picture Card Strategy',
                message: 'Hold your picture cards (8/9/10)! They are control weapons, not early loot.',
                category: 'strategy',
            });
        }

        // Endgame picture card advantage
        if (state.deck.length === 0 && pictureCards.length > 0) {
            tips.push({
                priority: 90,
                title: '🏆 Endgame Advantage!',
                message: 'You have the last picture card! Play it at the end to take ALL table cards.',
                category: 'strategy',
            });
        }
    }

    // Check for "easy sum" warning
    for (const card of normalCards) {
        if (!isPictureCard(card)) {
            const cardValue = card.value;
            // Check if dropping would create easy capture for opponent
            const newTableSum = table.filter(c => !isPictureCard(c)).reduce((s, c) => s + c.value, 0) + cardValue;
            if (newTableSum >= 2 && newTableSum <= 7) {
                const captures = findValidCaptures(card, table);
                if (captures.length === 0) {
                    tips.push({
                        priority: 60,
                        title: '⚠️ Careful When Dropping!',
                        message: `Your ${card.rank} would create a table sum of ${newTableSum} - easy for opponent!`,
                        category: 'warning',
                    });
                }
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
    const hasCapture = hand.some(card => findValidCaptures(card, table).length > 0 || (isPictureCard(card) && table.length > 0));
    if (!hasCapture && hand.length > 0) {
        // Find best card to drop
        const dropPriority = hand
            .filter(c => !isPictureCard(c))
            .sort((a, b) => {
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
                message: `No capture possible. The ${bestDrop.rank} is the safest card to drop.`,
                category: 'info',
            });
        }
    }

    // Sort by priority and return the best tip
    tips.sort((a, b) => b.priority - a.priority);
    return tips[0] || null;
}

/**
 * Get a random general strategy tip for display
 */
export function getRandomStrategyTip(): Tip {
    const strategies: Tip[] = [
        {
            priority: 0,
            title: '🎴 Picture Cards = Control',
            message: 'NEVER play 8/9/10 immediately. They are reset buttons, Chkobba blockers, and endgame weapons.',
            category: 'strategy',
        },
        {
            priority: 0,
            title: '❌ No Easy Sums',
            message: 'Avoid combinations like 3+4, 2+5, 1+6 on the table. Better to leave single cards or totals >7.',
            category: 'strategy',
        },
        {
            priority: 0,
            title: '7️⃣ Seven Memory',
            message: 'Track the 7♦ or lose! Every played seven changes the game.',
            category: 'strategy',
        },
        {
            priority: 0,
            title: '🅰️ Ace is a Tool',
            message: 'Perfect for snatching single cards. Never play it hoping for Chkobba!',
            category: 'strategy',
        },
        {
            priority: 0,
            title: '🏆 Endgame Checkmate',
            message: 'Last picture card = intentionally leave cards, then take EVERYTHING at the end.',
            category: 'strategy',
        },
        {
            priority: 0,
            title: '🧠 Play Calculatively',
            message: 'Play avoidant, cold, calculated. This is brutally effective against intuitive players.',
            category: 'strategy',
        },
        {
            priority: 0,
            title: '💎 Diamond Priority',
            message: 'Diamond cards score points! Especially the 7♦ is worth gold.',
            category: 'strategy',
        },
        {
            priority: 0,
            title: '🃏 Last Capture Rule',
            message: 'Whoever captures last gets all remaining table cards!',
            category: 'info',
        },
    ];

    return strategies[Math.floor(Math.random() * strategies.length)];
}
