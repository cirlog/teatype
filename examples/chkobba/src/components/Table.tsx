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
import CardComponent from './Card';

// Types
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
