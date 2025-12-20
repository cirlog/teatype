/**
 * Table component showing cards in play
 */

import React from 'react';
import CardComponent from './Card';
import { Card } from '../types/Card';
import { AnimationState } from '../types/GameState';

interface TableProps {
    cards: Card[];
    selectedCards: Card[];
    validCaptures: Card[][];
    onCardSelect?: (card: Card) => void;
    disabled?: boolean;
    animatingCardIds?: string[];
    animationType?: AnimationState['type'];
}

const Table: React.FC<TableProps> = ({
    cards,
    selectedCards,
    validCaptures,
    onCardSelect,
    disabled = false,
    animatingCardIds = [],
    animationType = 'none',
}) => {
    // Flatten valid captures to see which cards can be captured
    const capturableCardIds = new Set(validCaptures.flat().map((c) => c.id));
    const animatingSet = new Set(animatingCardIds);

    return (
        <div className={`table ${animationType !== 'none' ? `table--animation-${animationType}` : ''}`}>
            <div className='table__felt'>
                <div className='table__cards'>
                    {cards.length === 0 ? (
                        <div className='table__empty'>Table is empty</div>
                    ) : (
                        cards.map((card, index) => (
                            <div
                                key={card.id}
                                className={`table__card ${animatingSet.has(card.id) ? 'table__card--animating' : ''}`}
                                style={
                                    {
                                        '--card-index': index,
                                        '--total-cards': cards.length,
                                    } as React.CSSProperties
                                }
                            >
                                <CardComponent
                                    card={card}
                                    selected={selectedCards.some((sc) => sc.id === card.id)}
                                    highlighted={capturableCardIds.has(card.id)}
                                    onClick={onCardSelect && !disabled ? () => onCardSelect(card) : undefined}
                                    disabled={disabled || !capturableCardIds.has(card.id)}
                                    animating={animatingSet.has(card.id)}
                                />
                            </div>
                        ))
                    )}
                </div>
            </div>
            <div className='table__label'>Table ({cards.length} cards)</div>
        </div>
    );
};

export default Table;
