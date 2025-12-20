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

interface iHandProps {
    cards: iCard[];
    isHuman: boolean;
    selectedCard: iCard | null;
    onCardSelect?: (card: iCard) => void;
    disabled?: boolean;
    animatingCardId?: string;
}

const Hand: React.FC<iHandProps> = ({
    cards,
    isHuman,
    selectedCard,
    onCardSelect,
    disabled = false,
    animatingCardId,
}) => {
    return (
        <div className={`hand ${isHuman ? 'hand--human' : 'hand--npc'}`}>
            <div className='hand-cards'>
                {cards.map((card, index) => {
                    const isAnimating = animatingCardId === card.id;
                    return (
                        <div
                            key={card.id}
                            className={`hand-card ${isAnimating ? 'hand-card--animating' : ''}`}
                            style={
                                {
                                    '--card-index': index,
                                    zIndex: isAnimating ? 1000 : index,
                                } as React.CSSProperties
                            }
                        >
                            <CardComponent
                                card={card}
                                faceDown={!isHuman}
                                selected={selectedCard?.id === card.id}
                                onClick={isHuman && onCardSelect ? () => onCardSelect(card) : undefined}
                                disabled={disabled || !isHuman}
                                animating={isAnimating}
                            />
                        </div>
                    );
                })}
            </div>
            {!isHuman && <div className='hand-label'>NPC's Hand ({cards.length} cards)</div>}
            {isHuman && <div className='hand-label'>Your Hand</div>}
        </div>
    );
};

export default Hand;
