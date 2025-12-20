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
import { iCard } from '@/types/Card';

type tActionType = 'capture' | 'drop' | 'chkobba' | 'deal' | 'info';
type tDifficulty = 'easy' | 'medium' | 'hard' | 'expert';
type tGamePhase = 'menu' | 'playing' | 'roundEnd' | 'gameEnd';
type tPlayer = 'human' | 'npc';

interface iGameAction {
    cards?: iCard[];
    id: string;
    message: string;
    player: tPlayer | 'system';
    timestamp: number;
    type: tActionType;
}

interface iPlayerState {
    capturedCards: iCard[];
    chkobbas: number;
    hand: iCard[];
}

interface iAnimationState {
    cardId?: string;
    player?: tPlayer;
    targetCards?: string[];
    type: 'none' | 'card-play' | 'card-capture' | 'chkobba' | 'deal';
}

interface iGameState {
    actionLog: iGameAction[];
    animation: iAnimationState;
    currentPlayer: tPlayer;
    dealer: tPlayer;
    deck: iCard[];
    difficulty: tDifficulty;
    human: iPlayerState;
    humanTotalScore: number;
    isAnimating: boolean;
    lastCapturePlayer: tPlayer | null;
    message: string;
    npc: iPlayerState;
    npcTotalScore: number;
    phase: tGamePhase;
    roundNumber: number;
    selectedCard: iCard | null;
    selectedTableCards: iCard[];
    table: iCard[];
    targetScore: number;
    trainingMode: boolean;
    validCaptures: iCard[][];
}

interface iRoundScore {
    cards: number;        // +1 for majority (21+)
    chkobbas: number;     // +1 per chkobba
    diamonds: number;     // +1 for majority of diamonds
    setteDeneri: number;  // +1 for 7♦
    sevens: number;       // +1 for majority of 7s (3+)
    total: number;
}

interface iGameScores {
    human: iRoundScore;
    npc: iRoundScore;
}

/**
 * Create initial player state
 */
const createPlayerState = (): iPlayerState => {
    return {
        hand: [],
        capturedCards: [],
        chkobbas: 0,
    };
}

/**
 * Create initial game state
 */
const createInitialGameState = (): iGameState => {
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
const createGameAction = (player: tPlayer | 'system', type: tActionType, message: string, cards?: iCard[]): iGameAction => {
    return {
        id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        timestamp: Date.now(),
        player,
        type,
        message,
        cards,
    };
}

export {
    createInitialGameState,
    createGameAction,
    createPlayerState
};

export type {
    iAnimationState,
    iGameState,
    iPlayerState,
    iGameAction,
    iRoundScore,
    iGameScores,
    tPlayer,
    tDifficulty,
    tGamePhase
};
