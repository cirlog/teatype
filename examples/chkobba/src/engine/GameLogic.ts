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

// Types
import { iCard, canMakeChkobba, createDeck, shuffleDeck, getCardName } from '@/types/Card';
import { iGameState, tPlayer, iRoundScore, iGameScores, createPlayerState, createGameAction } from '@/types/GameState';

/**
 * Find all valid capture combinations for a played card
 * In French Chkobba, all cards capture by sum (J=8, Q=9, K=10)
 */
const findValidCaptures = (playedCard: iCard, tableCards: iCard[]): iCard[][] => {
    // All cards find combinations that sum to the card value
    const targetSum = playedCard.value;
    const combinations: iCard[][] = [];

    // Find all subsets of table cards that sum to targetSum
    const findSubsets = (
        remaining: iCard[],
        current: iCard[],
        currentSum: number,
        startIndex: number
    ) => {
        if (currentSum === targetSum && current.length > 0) {
            combinations.push([...current]);
        }
        if (currentSum >= targetSum) return;

        for (let i = startIndex; i < remaining.length; i++) {
            current.push(remaining[i]);
            findSubsets(remaining, current, currentSum + remaining[i].value, i + 1);
            current.pop();
        }
    };

    findSubsets(tableCards, [], 0, 0);
    return combinations;
}

/**
 * Check if the initial table setup allows immediate Chkobba
 * If so, we need to reshuffle
 */
const canMakeImmediateChkobba = (tableCards: iCard[]): boolean => {
    // Check if any single card from a potential hand could clear the table
    // This is simplified - just check if table sum could be achieved by 2-7, J, Q, or K
    const tableSum = tableCards.reduce((sum, c) => sum + c.value, 0);

    // If sum is achievable by any single card value 2-10
    if (tableSum >= 2 && tableSum <= 10) {
        return true;
    }
    return false;
}

/**
 * Deal initial cards for a new round
 */
const dealInitialCards = (state: iGameState): iGameState => {
    let deck = shuffleDeck(createDeck());
    let table: iCard[] = [];

    // Deal 4 cards to table, reshuffle if immediate Chkobba is possible
    let attempts = 0;
    do {
        deck = shuffleDeck(createDeck());
        table = deck.splice(0, 4);
        attempts++;
    } while (canMakeImmediateChkobba(table) && attempts < 100);

    // Deal 3 cards to each player
    const humanHand = deck.splice(0, 3);
    const npcHand = deck.splice(0, 3);

    // Non-dealer starts
    const currentPlayer: tPlayer = state.dealer === 'human' ? 'npc' : 'human';

    // Create action log entry
    const dealAction = createGameAction(
        'system',
        'deal',
        `New round! ${table.map(c => getCardName(c)).join(', ')} on the table.`,
        table
    );

    return {
        ...state,
        deck,
        table,
        human: {
            ...createPlayerState(),
            hand: humanHand,
        },
        npc: {
            ...createPlayerState(),
            hand: npcHand,
        },
        currentPlayer,
        lastCapturePlayer: null,
        phase: 'playing',
        message: currentPlayer === 'human' ? 'Your turn! Select a card to play.' : 'NPC is thinking...',
        selectedCard: null,
        selectedTableCards: [],
        validCaptures: [],
        actionLog: [...state.actionLog, dealAction],
        animation: { type: 'deal' },
    };
}

/**
 * Deal new hands when both players have played all cards
 */
const dealNewHands = (state: iGameState): iGameState => {
    if (state.deck.length === 0) {
        // No more cards - end round
        return endRound(state);
    }

    const deck = [...state.deck];
    const humanHand = deck.splice(0, 3);
    const npcHand = deck.splice(0, 3);

    return {
        ...state,
        deck,
        human: {
            ...state.human,
            hand: humanHand,
        },
        npc: {
            ...state.npc,
            hand: npcHand,
        },
        message: state.currentPlayer === 'human' ? 'New cards dealt. Your turn!' : 'New cards dealt. NPC is thinking...',
    };
}

/**
 * Execute a capture move
 */
const executeCapture = (state: iGameState, player: tPlayer, playedCard: iCard, capturedCards: iCard[]): iGameState => {
    const iPlayerState = state[player];
    const newHand = iPlayerState.hand.filter(c => c.id !== playedCard.id);
    const newCaptured = [...iPlayerState.capturedCards, playedCard, ...capturedCards];
    const newTable = state.table.filter(c => !capturedCards.some(cc => cc.id === c.id));

    // Check for Chkobba (table cleared by any card except Ace)
    let chkobbas = iPlayerState.chkobbas;
    let message = `${player === 'human' ? 'You' : 'NPC'} captured ${capturedCards.length + 1} cards!`;
    let actionType: 'capture' | 'chkobba' = 'capture';
    let logMessage = `${player === 'human' ? 'You' : 'NPC'} ${player === 'human' ? 'play' : 'plays'} ${getCardName(playedCard)} and captures ${capturedCards.map(c => getCardName(c)).join(', ')}.`;

    if (newTable.length === 0 && canMakeChkobba(playedCard)) {
        chkobbas++;
        message = `CHKOBBA! ${player === 'human' ? 'You' : 'NPC'} cleared the table!`;
        actionType = 'chkobba';
        logMessage = `🎯 CHKOBBA! ${player === 'human' ? 'You' : 'NPC'} clears the table with ${getCardName(playedCard)}!`;
    }

    const captureAction = createGameAction(player, actionType, logMessage, [playedCard, ...capturedCards]);

    const newState: iGameState = {
        ...state,
        table: newTable,
        [player]: {
            ...iPlayerState,
            hand: newHand,
            capturedCards: newCaptured,
            chkobbas,
        },
        lastCapturePlayer: player,
        message,
        selectedCard: null,
        selectedTableCards: [],
        validCaptures: [],
        actionLog: [...state.actionLog, captureAction],
        animation: {
            type: actionType === 'chkobba' ? 'chkobba' : 'card-capture',
            cardId: playedCard.id,
            targetCards: capturedCards.map(c => c.id),
            player,
        },
    };

    return switchTurn(newState);
}

/**
 * Execute a drop move (when no capture is possible)
 */
const executeDrop = (state: iGameState, player: tPlayer, playedCard: iCard): iGameState => {
    const iPlayerState = state[player];
    const newHand = iPlayerState.hand.filter(c => c.id !== playedCard.id);
    const newTable = [...state.table, playedCard];

    const dropAction = createGameAction(
        player,
        'drop',
        `${player === 'human' ? 'You' : 'NPC'} ${player === 'human' ? 'drop' : 'drops'} ${getCardName(playedCard)} on the table.`,
        [playedCard]
    );

    const newState: iGameState = {
        ...state,
        table: newTable,
        [player]: {
            ...iPlayerState,
            hand: newHand,
        },
        message: `${player === 'human' ? 'You' : 'NPC'} dropped a card.`,
        selectedCard: null,
        selectedTableCards: [],
        validCaptures: [],
        actionLog: [...state.actionLog, dropAction],
        animation: {
            type: 'card-play',
            cardId: playedCard.id,
            player,
        },
    };

    return switchTurn(newState);
}

/**
 * Switch to the next player's turn
 */
const switchTurn = (state: iGameState): iGameState => {
    const nextPlayer: tPlayer = state.currentPlayer === 'human' ? 'npc' : 'human';

    // Check if both players need new cards
    if (state.human.hand.length === 0 && state.npc.hand.length === 0) {
        if (state.deck.length === 0) {
            return endRound(state);
        }
        return dealNewHands({ ...state, currentPlayer: nextPlayer });
    }

    return {
        ...state,
        currentPlayer: nextPlayer,
        message: nextPlayer === 'human' ? 'Your turn!' : 'NPC is thinking...',
    };
}

/**
 * End the current round and calculate scores
 */
const endRound = (state: iGameState): iGameState => {
    // Last player to capture gets remaining table cards
    let finalState = { ...state };
    if (state.lastCapturePlayer && state.table.length > 0) {
        const player = state.lastCapturePlayer;
        finalState = {
            ...state,
            [player]: {
                ...state[player],
                capturedCards: [...state[player].capturedCards, ...state.table],
            },
            table: [],
        };
    }

    // Calculate scores
    const scores = calculateRoundScores(finalState);

    return {
        ...finalState,
        phase: 'roundEnd',
        humanTotalScore: state.humanTotalScore + scores.human.total,
        npcTotalScore: state.npcTotalScore + scores.npc.total,
        message: 'Round complete! Check the scores.',
    };
}

/**
 * Calculate round scores according to Tunisian rules
 */
const calculateRoundScores = (state: iGameState): iGameScores => {
    const humanCards = state.human.capturedCards;
    const npcCards = state.npc.capturedCards;

    // Count diamonds
    const humanDiamonds = humanCards.filter(c => c.suit === 'diamonds').length;
    const npcDiamonds = npcCards.filter(c => c.suit === 'diamonds').length;

    // Count sevens
    const humanSevens = humanCards.filter(c => c.rank === 7).length;
    const npcSevens = npcCards.filter(c => c.rank === 7).length;

    // Check for 7♦ (Sette di Deneri)
    const humanHasSetteDeneri = humanCards.some(c => c.suit === 'diamonds' && c.rank === 7);
    const npcHasSetteDeneri = npcCards.some(c => c.suit === 'diamonds' && c.rank === 7);

    const humanScore: iRoundScore = {
        cards: humanCards.length >= 21 ? 1 : 0,
        diamonds: humanDiamonds > npcDiamonds ? 1 : 0,
        setteDeneri: humanHasSetteDeneri ? 1 : 0,
        sevens: humanSevens >= 3 && humanSevens > npcSevens ? 1 : 0,
        chkobbas: state.human.chkobbas,
        total: 0,
    };
    humanScore.total = humanScore.cards + humanScore.diamonds + humanScore.setteDeneri +
        humanScore.sevens + humanScore.chkobbas;

    const npcScore: iRoundScore = {
        cards: npcCards.length >= 21 ? 1 : 0,
        diamonds: npcDiamonds > humanDiamonds ? 1 : 0,
        setteDeneri: npcHasSetteDeneri ? 1 : 0,
        sevens: npcSevens >= 3 && npcSevens > humanSevens ? 1 : 0,
        chkobbas: state.npc.chkobbas,
        total: 0,
    };
    npcScore.total = npcScore.cards + npcScore.diamonds + npcScore.setteDeneri +
        npcScore.sevens + npcScore.chkobbas;

    return { human: humanScore, npc: npcScore };
}

/**
 * Start a new round
 */
const startNewRound = (state: iGameState): iGameState => {
    // Check for game end
    if (state.humanTotalScore >= state.targetScore || state.npcTotalScore >= state.targetScore) {
        return {
            ...state,
            phase: 'gameEnd',
            message: state.humanTotalScore >= state.targetScore
                ? 'Congratulations! You won the game!'
                : 'The NPC won the game. Better luck next time!',
        };
    }

    // Alternate dealer
    const newDealer: tPlayer = state.dealer === 'human' ? 'npc' : 'human';

    const newState: iGameState = {
        ...state,
        dealer: newDealer,
        roundNumber: state.roundNumber + 1,
        human: createPlayerState(),
        npc: createPlayerState(),
    };

    return dealInitialCards(newState);
}

/**
 * Start a new game
 */
const startNewGame = (state: iGameState): iGameState => {
    const newState: iGameState = {
        ...state,
        phase: 'playing',
        deck: [],
        table: [],
        human: createPlayerState(),
        npc: createPlayerState(),
        currentPlayer: 'human',
        dealer: Math.random() < 0.5 ? 'human' : 'npc',
        lastCapturePlayer: null,
        roundNumber: 1,
        humanTotalScore: 0,
        npcTotalScore: 0,
        message: 'Starting new game...',
        selectedCard: null,
        selectedTableCards: [],
        validCaptures: [],
    };

    return dealInitialCards(newState);
}

/**
 * Validate and execute a human player's move
 */
const executeHumanMove = (state: iGameState, playedCard: iCard, selectedCapture: iCard[] | null): iGameState => {
    if (state.currentPlayer !== 'human') {
        return { ...state, message: "It's not your turn!" };
    }

    const validCaptures = findValidCaptures(playedCard, state.table);

    // If captures are possible, must capture
    if (validCaptures.length > 0) {
        if (!selectedCapture) {
            // iPlayer hasn't selected which capture yet
            return {
                ...state,
                selectedCard: playedCard,
                validCaptures,
                message: 'Select which cards to capture:',
            };
        }
        // Validate the selected capture
        const isValidSelection = validCaptures.some(vc =>
            vc.length === selectedCapture.length &&
            vc.every(c => selectedCapture.some(sc => sc.id === c.id))
        );
        if (!isValidSelection) {
            return { ...state, message: 'Invalid capture selection!' };
        }
        return executeCapture(state, 'human', playedCard, selectedCapture);
    }

    // No capture possible - drop the card
    return executeDrop(state, 'human', playedCard);
}

export {
    findValidCaptures,
    dealInitialCards,
    dealNewHands,
    executeCapture,
    executeDrop,
    switchTurn,
    endRound,
    calculateRoundScores,
    startNewRound,
    startNewGame,
    executeHumanMove,
};