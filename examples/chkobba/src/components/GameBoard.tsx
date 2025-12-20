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

import React from 'react';
import Hand from './Hand';
import Table from './Table';
import Deck from './Deck';
import ScoreDisplay from './ScoreDisplay';
import MessageLog from './MessageLog';
import TrainingTip from './TrainingTip';
import { iGameState } from '../types/GameState';
import { iCard } from '../types/Card';
import { iTip } from '../game/TrainingTips';

interface iGameBoardProps {
    state: iGameState;
    trainingTip: iTip | null;

    onCardSelect: (card: iCard) => void;
    onTableCardSelect: (card: iCard) => void;
    onConfirmCapture: () => void;
    onCancelSelection: () => void;
}

const GameBoard: React.FC<iGameBoardProps> = ({
    state,
    trainingTip,

    onCardSelect,
    onTableCardSelect,
    onConfirmCapture,
    onCancelSelection,
}) => {
    const isHumanTurn = state.currentPlayer === 'human';
    const hasSelectedCard = state.selectedCard !== null;
    const hasValidCaptures = state.validCaptures.length > 0;

    // Determine animation classes
    const getAnimationClass = (): string => {
        if (state.animation.type === 'none') return '';
        return `game-board--animating game-board--animation-${state.animation.type}`;
    };

    return (
        <div className={`game-board ${getAnimationClass()}`}>
            <div className='game-board-header'>
                <ScoreDisplay
                    humanScore={state.humanTotalScore}
                    npcScore={state.npcTotalScore}
                    humanChkobbas={state.human.chkobbas}
                    npcChkobbas={state.npc.chkobbas}
                    targetScore={state.targetScore}
                    roundNumber={state.roundNumber}
                />
            </div>

            <div className='game-board-body'>
                <div className='game-board-main'>
                    {/* NPC Hand */}
                    <div className='game-board-npc-area'>
                        <Hand
                            cards={state.npc.hand}
                            isHuman={false}
                            selectedCard={null}
                            disabled={true}
                            animatingCardId={state.animation.player === 'npc' ? state.animation.cardId : undefined}
                        />
                    </div>

                    {/* Center area with table and deck */}
                    <div className='game-board-center'>
                        <div className='game-board-deck-area'>
                            <Deck cardsRemaining={state.deck.length} />
                            <div className='game-board-captured'>
                                <div className='captured-pile'>
                                    <span className='captured-pile-label'>You captured:</span>
                                    <span className='captured-pile-count'>{state.human.capturedCards.length}</span>
                                </div>
                                <div className='captured-pile captured-pile--npc'>
                                    <span className='captured-pile-label'>NPC captured:</span>
                                    <span className='captured-pile-count'>{state.npc.capturedCards.length}</span>
                                </div>
                            </div>
                        </div>

                        <Table
                            cards={state.table}
                            selectedCards={state.selectedTableCards}
                            validCaptures={state.validCaptures}
                            onCardSelect={hasSelectedCard && hasValidCaptures ? onTableCardSelect : undefined}
                            disabled={!isHumanTurn || state.isAnimating}
                            animatingCardIds={state.animation.targetCards}
                            animationType={state.animation.type}
                            animatingPlayer={state.animation.player}
                        />
                    </div>

                    {/* Human Hand */}
                    <div className='game-board-human-area'>
                        <Hand
                            cards={state.human.hand}
                            isHuman={true}
                            selectedCard={state.selectedCard}
                            onCardSelect={onCardSelect}
                            disabled={!isHumanTurn || state.isAnimating || hasSelectedCard}
                            animatingCardId={state.animation.player === 'human' ? state.animation.cardId : undefined}
                        />

                        {/* Training tip */}
                        {state.trainingMode && isHumanTurn && (
                            <div className='game-board-training-tip'>
                                <TrainingTip tip={trainingTip} enabled={state.trainingMode} />
                            </div>
                        )}
                    </div>
                </div>

                {/* Message Log sidebar */}
                <div className='game-board-sidebar'>
                    <MessageLog actions={state.actionLog} />
                </div>
            </div>

            {/* Action bar */}
            <div className='game-board-actions'>
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
