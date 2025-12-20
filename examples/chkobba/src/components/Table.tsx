/**
 * Table component showing cards in play
 */

import React from 'react';
import CardComponent from './Card';
import { Card } from '../types/Card';

interface TableProps {
    cards: Card[];
    selectedCards: Card[];
    validCaptures: Card[][];
    onCardSelect?: (card: Card) => void;
    disabled?: boolean;
}

const Table: React.FC<TableProps> = ({ cards, selectedCards, validCaptures, onCardSelect, disabled = false }) => {
    // Flatten valid captures to see which cards can be captured
    const capturableCardIds = new Set(validCaptures.flat().map((c) => c.id));

    return (
        <div className='table'>
            <div className='table__felt'>
                <div className='table__cards'>
                    {cards.length === 0 ? (
                        <div className='table__empty'>Table is empty</div>
                    ) : (
                        cards.map((card, index) => (
                            <div
                                key={card.id}
                                className='table__card'
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
