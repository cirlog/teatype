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
                        title: '🎯 CHKOBBA MÖGLICH!',
                        message: `Spiele die ${card.rank} um alle Karten zu nehmen und einen Chkobba-Punkt zu bekommen!`,
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
                message: `Du kannst die 7♦ nehmen - das ist ein garantierter Punkt!`,
                category: 'opportunity',
            });
        }

        // Check for capturing multiple 7s
        const capturedSevens = captures.flat().filter(c => c.rank === 7);
        if (capturedSevens.length >= 2) {
            tips.push({
                priority: 85,
                title: '7️⃣ Siebener-Gelegenheit',
                message: `Du kannst ${capturedSevens.length} Siebener auf einmal nehmen!`,
                category: 'opportunity',
            });
        }

        // Check for capturing multiple diamonds
        const capturedDiamonds = captures.flat().filter(c => c.suit === 'diamonds');
        if (capturedDiamonds.length >= 3) {
            tips.push({
                priority: 80,
                title: '♦ Karo-Sammlung',
                message: `Gute Chance ${capturedDiamonds.length} Karo-Karten zu sammeln!`,
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
                title: '⚠️ Bildkarten-Strategie',
                message: 'Halte deine Bildkarten (8/9/10) zurück! Sie sind Kontroll-Waffen, nicht frühe Beute.',
                category: 'strategy',
            });
        }

        // Endgame picture card advantage
        if (state.deck.length === 0 && pictureCards.length > 0) {
            tips.push({
                priority: 90,
                title: '🏆 Endgame-Vorteil!',
                message: 'Du hast die letzte Bildkarte! Spiele sie zum Schluss um ALLE Tischkarten zu bekommen.',
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
                        title: '⚠️ Vorsicht beim Ablegen!',
                        message: `Die ${card.rank} würde eine Tischsumme von ${newTableSum} erzeugen - leicht für den Gegner!`,
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
                title: '🅰️ Ass als Werkzeug',
                message: 'Das Ass kann einzelne Karten wegschnappen - perfekt zum Zerstören gefährlicher Tischbilder!',
                category: 'info',
            });
        }
    }

    // 7er Memory tip
    const humanSevens = state.human.capturedCards.filter(c => c.rank === 7).length;
    const npcSevens = state.npc.capturedCards.filter(c => c.rank === 7).length;
    const tableSevens = table.filter(c => c.rank === 7).length;

    if (humanSevens < npcSevens && tableSevens > 0) {
        tips.push({
            priority: 75,
            title: '7️⃣ Siebener-Aufholjagd',
            message: `Der Gegner führt ${npcSevens}:${humanSevens} bei Siebenern. Versuche die 7 auf dem Tisch zu holen!`,
            category: 'warning',
        });
    }

    // Diamond majority tracking
    const humanDiamonds = state.human.capturedCards.filter(c => c.suit === 'diamonds').length;
    const npcDiamonds = state.npc.capturedCards.filter(c => c.suit === 'diamonds').length;

    if (npcDiamonds > humanDiamonds + 2) {
        tips.push({
            priority: 65,
            title: '♦ Karo-Rückstand',
            message: `Gegner führt ${npcDiamonds}:${humanDiamonds} bei Karos. Priorisiere Karo-Karten!`,
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
                title: '📊 Kartenmehrheit',
                message: `Der Gegner hat ${npcCards} Karten, du nur ${humanCards}. Nimm mehr Karten!`,
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
                title: '📤 Ablegen',
                message: `Kein Stechen möglich. Die ${bestDrop.rank} ist die sicherste Karte zum Ablegen.`,
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
            title: '🎴 Bildkarten = Kontrolle',
            message: '8/9/10 NIE sofort spielen. Sie sind Reset-Knöpfe, Chkobba-Blocker und Endgame-Waffen.',
            category: 'strategy',
        },
        {
            priority: 0,
            title: '❌ Keine einfachen Summen',
            message: 'Vermeide Kombinationen wie 3+4, 2+5, 1+6 auf dem Tisch. Lieber einzelne Karten oder >5.',
            category: 'strategy',
        },
        {
            priority: 0,
            title: '7️⃣ Siebener-Memory',
            message: '7♦ merken oder sterben! Jeder gespielte 7er verändert das Spiel.',
            category: 'strategy',
        },
        {
            priority: 0,
            title: '🅰️ Ass ist ein Werkzeug',
            message: 'Perfekt zum Wegnehmen einzelner Karten. Nie auf Chkobba spielen!',
            category: 'strategy',
        },
        {
            priority: 0,
            title: '🏆 Endgame-Checkmate',
            message: 'Letzte Bildkarte = lass bewusst Karten liegen, nimm am Schluss ALLES.',
            category: 'strategy',
        },
        {
            priority: 0,
            title: '🧠 Rechnerisch spielen',
            message: 'Spiele vermeidend, kalt, rechnerisch. Das ist brutal effektiv gegen intuitive Spieler.',
            category: 'strategy',
        },
        {
            priority: 0,
            title: '💎 Karo-Priorität',
            message: 'Karo-Karten bringen Punkte! Besonders die 7♦ ist Gold wert.',
            category: 'strategy',
        },
        {
            priority: 0,
            title: '🃏 Letzte Stich-Regel',
            message: 'Wer zuletzt sticht, bekommt alle verbleibenden Tischkarten!',
            category: 'info',
        },
    ];

    return strategies[Math.floor(Math.random() * strategies.length)];
}
