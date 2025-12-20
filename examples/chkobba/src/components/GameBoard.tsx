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

// React imports
import React from 'react';

// Components
import Hand from '@/components/Hand';
import Table from '@/components/Table';
import Deck from '@/components/Deck';
import ScoreDisplay from '@/components/ScoreDisplay';
import MessageLog from '@/components/MessageLog';
import TrainingTip from '@/components/TrainingTip';

// Types
import { iTip } from '@/engine/TrainingTips';
import { iGameState } from '@/types/GameState';
import { iCard } from '@/types/Card';

interface iGameBoardProps {
    state: iGameState;
    trainingTip: iTip | null;

    onCardSelect: (card: iCard) => void;
    onTableCardSelect: (card: iCard) => void;
    onConfirmCapture: () => void;
    onCancelSelection: () => void;
}

const GameBoard: React.FC<iGameBoardProps> = (props) => {
    const isHumanTurn = props.state.currentPlayer === 'human';
    const hasSelectedCard = props.state.selectedCard !== null;
    const hasValidCaptures = props.state.validCaptures.length > 0;

    // Determine animation classes
    const getAnimationClass = (): string => {
        if (props.state.animation.type === 'none') return '';
        return `game-board--animating game-board--animation-${props.state.animation.type}`;
    };

    return (
        <div className={`game-board ${getAnimationClass()}`}>
            <div className='game-board-header'>
                <ScoreDisplay
                    humanScore={props.state.humanTotalScore}
                    npcScore={props.state.npcTotalScore}
                    humanChkobbas={props.state.human.chkobbas}
                    npcChkobbas={props.state.npc.chkobbas}
                    targetScore={props.state.targetScore}
                    roundNumber={props.state.roundNumber}
                />
            </div>

            <div className='game-board-body'>
                <div className='game-board-main'>
                    {/* NPC Hand */}
                    <div className='game-board-npc-area'>
                        <Hand
                            cards={props.state.npc.hand}
                            isHuman={false}
                            selectedCard={null}
                            disabled={true}
                            animatingCardId={
                                props.state.animation.player === 'npc' ? props.state.animation.cardId : undefined
                            }
                        />
                    </div>

                    {/* Center area with table and deck */}
                    <div className='game-board-center'>
                        <div className='game-board-deck-area'>
                            <Deck cardsRemaining={props.state.deck.length} />
                            <div className='game-board-captured'>
                                <div className='captured-pile'>
                                    <span className='captured-pile-label'>You captured:</span>
                                    <span className='captured-pile-count'>
                                        {props.state.human.capturedCards.length}
                                    </span>
                                </div>
                                <div className='captured-pile captured-pile--npc'>
                                    <span className='captured-pile-label'>NPC captured:</span>
                                    <span className='captured-pile-count'>{props.state.npc.capturedCards.length}</span>
                                </div>
                            </div>
                        </div>

                        <Table
                            cards={props.state.table}
                            selectedCards={props.state.selectedTableCards}
                            validCaptures={props.state.validCaptures}
                            onCardSelect={hasSelectedCard && hasValidCaptures ? props.onTableCardSelect : undefined}
                            disabled={!isHumanTurn || props.state.isAnimating}
                            animatingCardIds={props.state.animation.targetCards}
                            animationType={props.state.animation.type}
                            animatingPlayer={props.state.animation.player}
                        />
                    </div>

                    {/* Human Hand */}
                    <div className='game-board-human-area'>
                        <Hand
                            cards={props.state.human.hand}
                            isHuman={true}
                            selectedCard={props.state.selectedCard}
                            onCardSelect={props.onCardSelect}
                            disabled={!isHumanTurn || props.state.isAnimating || hasSelectedCard}
                            animatingCardId={
                                props.state.animation.player === 'human' ? props.state.animation.cardId : undefined
                            }
                        />

                        {/* Training tip */}
                        {props.state.trainingMode && isHumanTurn && (
                            <div className='game-board-training-tip'>
                                <TrainingTip tip={props.trainingTip} enabled={props.state.trainingMode} />
                            </div>
                        )}
                    </div>
                </div>

                {/* Message Log sidebar */}
                <div className='game-board-sidebar'>
                    <MessageLog actions={props.state.actionLog} />
                </div>
            </div>

            {/* Action bar */}
            <div className='game-board-actions'>
                <div className={`message ${props.state.message.includes('CHKOBBA') ? 'message--chkobba' : ''}`}>
                    {props.state.message}
                </div>

                {hasSelectedCard && hasValidCaptures && props.state.validCaptures.length > 1 && (
                    <div className='action-buttons'>
                        <span className='action-hint'>Click table cards to select, then confirm</span>
                        <button
                            className='btn btn--primary'
                            onClick={props.onConfirmCapture}
                            disabled={props.state.selectedTableCards.length === 0}
                        >
                            Confirm Capture
                        </button>
                        <button className='btn btn--secondary' onClick={props.onCancelSelection}>
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
