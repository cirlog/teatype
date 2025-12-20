/**
 * Game state types for Tunisian Chkobba
 */

import { Card } from './Card';

export type Player = 'human' | 'npc';
export type Difficulty = 'easy' | 'medium' | 'hard' | 'expert';
export type GamePhase = 'menu' | 'playing' | 'roundEnd' | 'gameEnd';

export interface PlayerState {
    hand: Card[];
    capturedCards: Card[];
    chkobbas: number;
}

export interface GameState {
    phase: GamePhase;
    difficulty: Difficulty;
    deck: Card[];
    table: Card[];
    human: PlayerState;
    npc: PlayerState;
    currentPlayer: Player;
    dealer: Player;
    lastCapturePlayer: Player | null;
    roundNumber: number;
    humanTotalScore: number;
    npcTotalScore: number;
    targetScore: number;
    message: string;
    selectedCard: Card | null;
    selectedTableCards: Card[];
    validCaptures: Card[][];
    isAnimating: boolean;
}

export interface RoundScore {
    cards: number;        // +1 for majority (21+)
    diamonds: number;     // +1 for majority of diamonds
    setteDeneri: number;  // +1 for 7♦
    sevens: number;       // +1 for majority of 7s (3+)
    chkobbas: number;     // +1 per chkobba
    total: number;
}

export interface GameScores {
    human: RoundScore;
    npc: RoundScore;
}

/**
 * Create initial player state
 */
export function createPlayerState(): PlayerState {
    return {
        hand: [],
        capturedCards: [],
        chkobbas: 0,
    };
}

/**
 * Create initial game state
 */
export function createInitialGameState(): GameState {
    return {
        phase: 'menu',
        difficulty: 'medium',
        deck: [],
        table: [],
        human: createPlayerState(),
        npc: createPlayerState(),
        currentPlayer: 'human',
        dealer: 'npc',
        lastCapturePlayer: null,
        roundNumber: 0,
        humanTotalScore: 0,
        npcTotalScore: 0,
        targetScore: 11,
        message: 'Welcome to Chkobba!',
        selectedCard: null,
        selectedTableCards: [],
        validCaptures: [],
        isAnimating: false,
    };
}
