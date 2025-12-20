/**
 * Main game board component
 */

import React from 'react';
import Hand from './Hand';
import Table from './Table';
import Deck from './Deck';
import ScoreDisplay from './ScoreDisplay';
import { GameState } from '../types/GameState';
import { Card } from '../types/Card';

interface GameBoardProps {
    state: GameState;
    onCardSelect: (card: Card) => void;
    onTableCardSelect: (card: Card) => void;
    onConfirmCapture: () => void;
    onCancelSelection: () => void;
}

const GameBoard: React.FC<GameBoardProps> = ({
    state,
    onCardSelect,
    onTableCardSelect,
    onConfirmCapture,
    onCancelSelection,
}) => {
    const isHumanTurn = state.currentPlayer === 'human';
    const hasSelectedCard = state.selectedCard !== null;
    const hasValidCaptures = state.validCaptures.length > 0;

    return (
        <div className='game-board'>
            <div className='game-board__header'>
                <ScoreDisplay
                    humanScore={state.humanTotalScore}
                    npcScore={state.npcTotalScore}
                    humanChkobbas={state.human.chkobbas}
                    npcChkobbas={state.npc.chkobbas}
                    targetScore={state.targetScore}
                    roundNumber={state.roundNumber}
                />
            </div>

            <div className='game-board__main'>
                {/* NPC Hand */}
                <div className='game-board__npc-area'>
                    <Hand cards={state.npc.hand} isHuman={false} selectedCard={null} disabled={true} />
                </div>

                {/* Center area with table and deck */}
                <div className='game-board__center'>
                    <div className='game-board__deck-area'>
                        <Deck cardsRemaining={state.deck.length} />
                        <div className='game-board__captured'>
                            <div className='captured-pile'>
                                <span className='captured-pile__label'>Your captures</span>
                                <span className='captured-pile__count'>{state.human.capturedCards.length}</span>
                            </div>
                            <div className='captured-pile captured-pile--npc'>
                                <span className='captured-pile__label'>NPC captures</span>
                                <span className='captured-pile__count'>{state.npc.capturedCards.length}</span>
                            </div>
                        </div>
                    </div>

                    <Table
                        cards={state.table}
                        selectedCards={state.selectedTableCards}
                        validCaptures={state.validCaptures}
                        onCardSelect={hasSelectedCard && hasValidCaptures ? onTableCardSelect : undefined}
                        disabled={!isHumanTurn || state.isAnimating}
                    />
                </div>

                {/* Human Hand */}
                <div className='game-board__human-area'>
                    <Hand
                        cards={state.human.hand}
                        isHuman={true}
                        selectedCard={state.selectedCard}
                        onCardSelect={onCardSelect}
                        disabled={!isHumanTurn || state.isAnimating || hasSelectedCard}
                    />
                </div>
            </div>

            {/* Action bar */}
            <div className='game-board__actions'>
                <div className={`message ${state.message.includes('CHKOBBA') ? 'message--chkobba' : ''}`}>
                    {state.message}
                </div>

                {hasSelectedCard && hasValidCaptures && state.validCaptures.length > 1 && (
                    <div className='action-buttons'>
                        <span className='action-hint'>Click table cards to select, then confirm</span>
                        <button
                            className='btn btn--primary'
                            onClick={onConfirmCapture}
                            disabled={state.selectedTableCards.length === 0}
                        >
                            Confirm Capture
                        </button>
                        <button className='btn btn--secondary' onClick={onCancelSelection}>
                            Cancel
                        </button>
                    </div>
                )}

                {!isHumanTurn && (
                    <div className='thinking-indicator'>
                        <span className='thinking-dot'></span>
                        <span className='thinking-dot'></span>
                        <span className='thinking-dot'></span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default GameBoard;
