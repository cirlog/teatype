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

// Types
import { iCard, getSuitColor } from '../types/Card';

interface iCardProps {
    card: iCard;
    faceDown?: boolean;
    selected?: boolean;
    highlighted?: boolean;
    onClick?: () => void;
    disabled?: boolean;
    small?: boolean;
    animating?: boolean;
}

/**
 * Get local card image URL
 * Card codes: A, 2-7, J, Q, K + S (spades), H (hearts), D (diamonds), C (clubs)
 * Images stored in /public/cards/
 */
function getCardImageUrl(card: iCard): string {
    // Map rank to image code
    const rankCode = card.rank === 1 ? 'A' : card.rank.toString();
    const suitCode = {
        spades: 'S',
        hearts: 'H',
        diamonds: 'D',
        clubs: 'C',
    }[card.suit];

    return `/cards/${rankCode}${suitCode}.png`;
}

const CARD_BACK_URL = '/cards/back.png';

const CardComponent: React.FC<iCardProps> = ({
    card,
    faceDown = false,
    selected = false,
    highlighted = false,
    onClick,
    disabled = false,
    small = false,
    animating = false,
}) => {
    const imageUrl = faceDown ? CARD_BACK_URL : getCardImageUrl(card);
    const color = getSuitColor(card.suit);

    const handleClick = () => {
        if (!disabled && onClick) {
            onClick();
        }
    };

    const cardClass = [
        'card',
        selected ? 'card--selected' : '',
        highlighted ? 'card--highlighted' : '',
        disabled ? 'card--disabled' : '',
        small ? 'card--small' : '',
        faceDown ? 'card--facedown' : '',
        color === 'red' ? 'card--red' : 'card--black',
        animating ? 'card--animating' : '',
    ]
        .filter(Boolean)
        .join(' ');

    return (
        <div className={cardClass} onClick={handleClick}>
            <img
                src={imageUrl}
                alt={faceDown ? 'Card back' : `${card.rank} of ${card.suit}`}
                className='card-image'
                draggable={false}
            />
            {selected && <div className='card-selection-indicator' />}
            {highlighted && <div className='card-highlight-indicator' />}
        </div>
    );
};

export default CardComponent;
