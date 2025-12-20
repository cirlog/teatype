/**
 * Table component showing cards in play
 */

import React from 'react';
import CardComponent from './Card';
import { iCard } from '../types/Card';
import { iAnimationState, tPlayer } from '../types/GameState';

interface iTableProps {
    cards: iCard[];
    selectedCards: iCard[];
    validCaptures: iCard[][];
    onCardSelect?: (card: iCard) => void;
    disabled?: boolean;
    animatingCardIds?: string[];
    animationType?: iAnimationState['type'];
    animatingPlayer?: tPlayer;
}

const Table: React.FC<iTableProps> = ({
    cards,
    selectedCards,
    validCaptures,
    onCardSelect,
    disabled = false,
    animatingCardIds = [],
    animationType = 'none',
    animatingPlayer,
}) => {
    // Flatten valid captures to see which cards can be captured
    const capturableCardIds = new Set(validCaptures.flat().map((c) => c.id));
    const animatingSet = new Set(animatingCardIds);

    // Build table class with animation context
    const tableClass = [
        'table',
        animationType !== 'none' ? `table--animation-${animationType}` : '',
        animatingPlayer ? `table--capture-${animatingPlayer}` : '',
    ]
        .filter(Boolean)
        .join(' ');

    return (
        <div className={tableClass}>
            <div className='table-felt'>
                <div className='table-cards'>
                    {cards.length === 0 ? (
                        <div className='table-empty'>Table is empty</div>
                    ) : (
                        cards.map((card, index) => (
                            <div
                                key={card.id}
                                className={`table-card ${animatingSet.has(card.id) ? 'table-card--animating' : ''}`}
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
            <div className='table-label'>Table ({cards.length} cards)</div>
        </div>
    );
};

export default Table;
