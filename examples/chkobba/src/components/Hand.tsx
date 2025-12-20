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
import CardComponent from '@/components/Card';

// Types
import { iCard } from '@/types/Card';

interface iHandProps {
    animatingCardId?: string;
    cards: iCard[];
    disabled?: boolean;
    isHuman: boolean;
    selectedCard: iCard | null;

    onCardSelect?: (card: iCard) => void;
}

const Hand: React.FC<iHandProps> = (props) => {
    const disabled = props.disabled ?? false;

    return (
        <div className={`hand ${props.isHuman ? 'hand--human' : 'hand--npc'}`}>
            <div className='hand-cards'>
                {props.cards.map((card, index) => {
                    const isAnimating = props.animatingCardId === card.id;
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
                                faceDown={!props.isHuman}
                                selected={props.selectedCard?.id === card.id}
                                onClick={
                                    props.isHuman && props.onCardSelect ? () => props.onCardSelect(card) : undefined
                                }
                                disabled={disabled || !props.isHuman}
                                animating={isAnimating}
                            />
                        </div>
                    );
                })}
            </div>
            {!props.isHuman && <div className='hand-label'>NPC's Hand ({props.cards.length} cards)</div>}
            {props.isHuman && <div className='hand-label'>Your Hand</div>}
        </div>
    );
};

export default Hand;
