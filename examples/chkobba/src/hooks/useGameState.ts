/**
 * Custom hook for managing game state
 */

import { useState, useCallback, useEffect, useRef, useMemo } from 'react';
import { iGameState, tDifficulty, createInitialGameState } from '../types/GameState';
import { iCard } from '../types/Card';
import {
    startNewGame,
    startNewRound,
    findValidCaptures,
    executeCapture,
    executeDrop,
    calculateRoundScores
} from '../game/GameLogic';
import { executeNPCTurn, getNPCThinkingTime } from '../game/NPCAi';
import { getTrainingTip, iTip } from '../game/TrainingTips';

export function useGameState() {
    const [state, setState] = useState<iGameState>(createInitialGameState());
    const [roundScores, setRoundScores] = useState<ReturnType<typeof calculateRoundScores> | null>(null);
    const npcTurnRef = useRef<boolean>(false);

    // Calculate training tip when it's human's turn
    const trainingTip: iTip | null = useMemo(() => {
        if (state.trainingMode && state.currentPlayer === 'human' && state.phase === 'playing') {
            return getTrainingTip(state);
        }
        return null;
    }, [state.trainingMode, state.currentPlayer, state.phase, state.human.hand, state.table]);

    // Clear animation after a delay
    useEffect(() => {
        if (state.animation.type !== 'none') {
            const timeout = setTimeout(() => {
                setState(prev => ({
                    ...prev,
                    animation: { type: 'none' },
                }));
            }, 600);
            return () => clearTimeout(timeout);
        }
    }, [state.animation]);

    // Handle NPC turn
    useEffect(() => {
        // Check if it's NPC's turn and they have cards to play
        const isNpcTurn = state.phase === 'playing' &&
            state.currentPlayer === 'npc' &&
            state.npc.hand.length > 0;

        if (isNpcTurn && !npcTurnRef.current) {
            npcTurnRef.current = true;

            const thinkingTime = getNPCThinkingTime(state.difficulty);

            const timeout = setTimeout(() => {
                setState(prev => {
                    // Double-check it's still NPC's turn
                    if (prev.currentPlayer !== 'npc' || prev.npc.hand.length === 0) {
                        npcTurnRef.current = false;
                        return prev;
                    }
                    const newState = executeNPCTurn(prev);
                    npcTurnRef.current = false;
                    return newState;
                });
            }, thinkingTime);

            return () => {
                clearTimeout(timeout);
                npcTurnRef.current = false;
            };
        }
    }, [state.currentPlayer, state.phase, state.npc.hand.length, state.difficulty]);

    // Calculate round scores when round ends
    useEffect(() => {
        if (state.phase === 'roundEnd') {
            const scores = calculateRoundScores(state);
            setRoundScores(scores);
        }
    }, [state.phase]);

    const setDifficulty = useCallback((difficulty: tDifficulty) => {
        setState(prev => ({ ...prev, difficulty }));
    }, []);

    const setTargetScore = useCallback((targetScore: number) => {
        setState(prev => ({ ...prev, targetScore }));
    }, []);

    const setTrainingMode = useCallback((trainingMode: boolean) => {
        setState(prev => ({ ...prev, trainingMode }));
    }, []);

    const handleStartGame = useCallback(() => {
        setState(prev => startNewGame(prev));
    }, []);

    const handleContinueRound = useCallback(() => {
        setRoundScores(null);
        setState(prev => startNewRound(prev));
    }, []);

    const handlePlayAgain = useCallback(() => {
        setRoundScores(null);
        setState(prev => ({
            ...createInitialGameState(),
            difficulty: prev.difficulty,
            targetScore: prev.targetScore,
            trainingMode: prev.trainingMode,
        }));
        setTimeout(() => {
            setState(prev => startNewGame(prev));
        }, 100);
    }, []);

    const handleMainMenu = useCallback(() => {
        setRoundScores(null);
        setState(prev => ({
            ...createInitialGameState(),
            difficulty: prev.difficulty,
            targetScore: prev.targetScore,
            trainingMode: prev.trainingMode,
        }));
    }, []);

    const handleCardSelect = useCallback((card: iCard) => {
        if (state.currentPlayer !== 'human' || state.isAnimating) return;

        const validCaptures = findValidCaptures(card, state.table);

        // No captures possible: drop the card
        if (validCaptures.length === 0) {
            setState(prev => executeDrop(prev, 'human', card));
            return;
        }

        // Single capture option: execute immediately
        if (validCaptures.length === 1) {
            setState(prev => executeCapture(prev, 'human', card, validCaptures[0]));
            return;
        }

        // Multiple capture options: let player choose
        setState(prev => ({
            ...prev,
            selectedCard: card,
            validCaptures,
            selectedTableCards: [],
            message: 'Multiple captures possible. Select cards to capture:',
        }));
    }, [state.currentPlayer, state.isAnimating, state.table]);

    const handleTableCardSelect = useCallback((card: iCard) => {
        if (!state.selectedCard || state.validCaptures.length === 0) return;

        setState(prev => {
            const isSelected = prev.selectedTableCards.some(c => c.id === card.id);
            let newSelected: iCard[];

            if (isSelected) {
                newSelected = prev.selectedTableCards.filter(c => c.id !== card.id);
            } else {
                newSelected = [...prev.selectedTableCards, card];
            }

            return {
                ...prev,
                selectedTableCards: newSelected,
            };
        });
    }, [state.selectedCard, state.validCaptures]);

    const handleConfirmCapture = useCallback(() => {
        if (!state.selectedCard || state.selectedTableCards.length === 0) return;

        // Validate that selected cards form a valid capture
        const isValid = state.validCaptures.some(vc =>
            vc.length === state.selectedTableCards.length &&
            vc.every(c => state.selectedTableCards.some(sc => sc.id === c.id))
        );

        if (!isValid) {
            setState(prev => ({
                ...prev,
                message: 'Invalid selection! Cards must sum to your card\'s value.',
            }));
            return;
        }

        setState(prev => executeCapture(prev, 'human', prev.selectedCard!, prev.selectedTableCards));
    }, [state.selectedCard, state.selectedTableCards, state.validCaptures]);

    const handleCancelSelection = useCallback(() => {
        setState(prev => ({
            ...prev,
            selectedCard: null,
            selectedTableCards: [],
            validCaptures: [],
            message: 'Your turn! Select a card to play.',
        }));
    }, []);

    return {
        state,
        roundScores,
        trainingTip,
        setDifficulty,
        setTargetScore,
        setTrainingMode,
        handleStartGame,
        handleContinueRound,
        handlePlayAgain,
        handleMainMenu,
        handleCardSelect,
        handleTableCardSelect,
        handleConfirmCapture,
        handleCancelSelection,
    };
}
