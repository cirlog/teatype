/**
 * Game state types for Tunisian Chkobba
 */

import { Card } from './Card';

export type Player = 'human' | 'npc';
export type Difficulty = 'easy' | 'medium' | 'hard' | 'expert';
export type GamePhase = 'menu' | 'playing' | 'roundEnd' | 'gameEnd';
export type ActionType = 'capture' | 'drop' | 'chkobba' | 'deal' | 'info' | 'picture-capture';

export interface GameAction {
    id: string;
    timestamp: number;
    player: Player | 'system';
    type: ActionType;
    message: string;
    cards?: Card[];
}

export interface PlayerState {
    hand: Card[];
    capturedCards: Card[];
    chkobbas: number;
}

export interface AnimationState {
    type: 'none' | 'card-play' | 'card-capture' | 'chkobba' | 'deal';
    cardId?: string;
    targetCards?: string[];
    player?: Player;
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
    trainingMode: boolean;
    actionLog: GameAction[];
    animation: AnimationState;
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
        trainingMode: false,
        actionLog: [],
        animation: { type: 'none' },
    };
}

/**
 * Create a new game action for the log
 */
export function createGameAction(
    player: Player | 'system',
    type: ActionType,
    message: string,
    cards?: Card[]
): GameAction {
    return {
        id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        timestamp: Date.now(),
        player,
        type,
        message,
        cards,
    };
}
