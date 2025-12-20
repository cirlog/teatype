/**
 * Game logic for Tunisian Chkobba
 * 
 * Key rules:
 * - Deck: 40 cards (WITH 8, 9, 10 - without J, Q, K)
 * - Picture cards (8/9/10): Take ALL cards from table, never make Chkobba
 * - Ace (1): Can capture but CANNOT make Chkobba
 * - Number cards (2-7): Can capture by sum, CAN make Chkobba
 * - Capturing is MANDATORY if possible
 * - Chkobba: Clearing table with a number card (2-7) = +1 point
 */

import { Card, isPictureCard, canMakeChkobba, createDeck, shuffleDeck, getCardName } from '../types/Card';
import { GameState, Player, RoundScore, GameScores, createPlayerState, createGameAction } from '../types/GameState';

/**
 * Find all valid capture combinations for a played card
 */
export function findValidCaptures(playedCard: Card, tableCards: Card[]): Card[][] {
    // Picture cards (8, 9, 10) take ALL cards from the table
    if (isPictureCard(playedCard)) {
        if (tableCards.length > 0) {
            return [tableCards]; // Only one option: take all
        }
        return []; // No cards to take
    }

    // For number cards (1-7), find combinations that sum to the card value
    const targetSum = playedCard.value;
    const combinations: Card[][] = [];

    // Find all subsets of table cards that sum to targetSum
    const findSubsets = (
        remaining: Card[],
        current: Card[],
        currentSum: number,
        startIndex: number
    ) => {
        if (currentSum === targetSum && current.length > 0) {
            combinations.push([...current]);
        }
        if (currentSum >= targetSum) return;

        for (let i = startIndex; i < remaining.length; i++) {
            // Skip picture cards - they can't be captured by sum
            if (isPictureCard(remaining[i])) continue;

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
export function canMakeImmediateChkobba(tableCards: Card[]): boolean {
    // Check if any single card from a potential hand could clear the table
    // This is simplified - just check if table sum could be achieved by any 2-7 card
    const tableSum = tableCards
        .filter(c => !isPictureCard(c))
        .reduce((sum, c) => sum + c.value, 0);

    // If table has only picture cards, or sum is achievable by 2-7
    if (tableCards.every(c => isPictureCard(c))) return false;
    if (tableSum >= 2 && tableSum <= 7 && tableCards.filter(c => !isPictureCard(c)).length === tableCards.length) {
        return true;
    }
    return false;
}

/**
 * Deal initial cards for a new round
 */
export function dealInitialCards(state: GameState): GameState {
    let deck = shuffleDeck(createDeck());
    let table: Card[] = [];

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
    const currentPlayer: Player = state.dealer === 'human' ? 'npc' : 'human';

    // Create action log entry
    const dealAction = createGameAction(
        'system',
        'deal',
        `Neue Runde! ${table.map(c => getCardName(c)).join(', ')} auf dem Tisch.`,
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
export function dealNewHands(state: GameState): GameState {
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
export function executeCapture(
    state: GameState,
    player: Player,
    playedCard: Card,
    capturedCards: Card[]
): GameState {
    const playerState = state[player];
    const newHand = playerState.hand.filter(c => c.id !== playedCard.id);
    const newCaptured = [...playerState.capturedCards, playedCard, ...capturedCards];
    const newTable = state.table.filter(c => !capturedCards.some(cc => cc.id === c.id));

    // Check for Chkobba (table cleared by a number card 2-7, not Ace, not picture card)
    let chkobbas = playerState.chkobbas;
    let message = `${player === 'human' ? 'You' : 'NPC'} captured ${capturedCards.length + 1} cards!`;
    let actionType: 'capture' | 'chkobba' | 'picture-capture' = isPictureCard(playedCard) ? 'picture-capture' : 'capture';
    let logMessage = `${player === 'human' ? 'Du' : 'NPC'} spielt ${getCardName(playedCard)} und nimmt ${capturedCards.map(c => getCardName(c)).join(', ')}.`;

    if (newTable.length === 0 && canMakeChkobba(playedCard)) {
        chkobbas++;
        message = `CHKOBBA! ${player === 'human' ? 'You' : 'NPC'} cleared the table!`;
        actionType = 'chkobba';
        logMessage = `🎯 CHKOBBA! ${player === 'human' ? 'Du' : 'NPC'} räumt den Tisch mit ${getCardName(playedCard)}!`;
    } else if (isPictureCard(playedCard)) {
        logMessage = `${player === 'human' ? 'Du' : 'NPC'} spielt Bildkarte ${getCardName(playedCard)} und nimmt ALLE Tischkarten!`;
    }

    const captureAction = createGameAction(player, actionType, logMessage, [playedCard, ...capturedCards]);

    const newState: GameState = {
        ...state,
        table: newTable,
        [player]: {
            ...playerState,
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
export function executeDrop(state: GameState, player: Player, playedCard: Card): GameState {
    const playerState = state[player];
    const newHand = playerState.hand.filter(c => c.id !== playedCard.id);
    const newTable = [...state.table, playedCard];

    const dropAction = createGameAction(
        player,
        'drop',
        `${player === 'human' ? 'Du' : 'NPC'} legt ${getCardName(playedCard)} ab.`,
        [playedCard]
    );

    const newState: GameState = {
        ...state,
        table: newTable,
        [player]: {
            ...playerState,
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
function switchTurn(state: GameState): GameState {
    const nextPlayer: Player = state.currentPlayer === 'human' ? 'npc' : 'human';

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
export function endRound(state: GameState): GameState {
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
export function calculateRoundScores(state: GameState): GameScores {
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

    const humanScore: RoundScore = {
        cards: humanCards.length >= 21 ? 1 : 0,
        diamonds: humanDiamonds > npcDiamonds ? 1 : 0,
        setteDeneri: humanHasSetteDeneri ? 1 : 0,
        sevens: humanSevens >= 3 && humanSevens > npcSevens ? 1 : 0,
        chkobbas: state.human.chkobbas,
        total: 0,
    };
    humanScore.total = humanScore.cards + humanScore.diamonds + humanScore.setteDeneri +
        humanScore.sevens + humanScore.chkobbas;

    const npcScore: RoundScore = {
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
export function startNewRound(state: GameState): GameState {
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
    const newDealer: Player = state.dealer === 'human' ? 'npc' : 'human';

    const newState: GameState = {
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
export function startNewGame(state: GameState): GameState {
    const newState: GameState = {
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
export function executeHumanMove(
    state: GameState,
    playedCard: Card,
    selectedCapture: Card[] | null
): GameState {
    if (state.currentPlayer !== 'human') {
        return { ...state, message: "It's not your turn!" };
    }

    const validCaptures = findValidCaptures(playedCard, state.table);

    // Picture card: must take all if there are cards
    if (isPictureCard(playedCard)) {
        if (state.table.length > 0) {
            return executeCapture(state, 'human', playedCard, state.table);
        }
        return executeDrop(state, 'human', playedCard);
    }

    // If captures are possible, must capture
    if (validCaptures.length > 0) {
        if (!selectedCapture) {
            // Player hasn't selected which capture yet
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
