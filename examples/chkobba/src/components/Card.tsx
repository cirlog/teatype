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
import { iCard, getSuitColor } from '@/types/Card';

interface iCardProps {
    animating?: boolean;
    card: iCard;
    disabled?: boolean;
    faceDown?: boolean;
    highlighted?: boolean;
    selected?: boolean;
    small?: boolean;

    onClick?: () => void;
}

const CARD_BACK_URL = '/cards/back.png';

/**
 * Get local card image URL
 * Card codes: A, 2-7, J, Q, K + S (spades), H (hearts), D (diamonds), C (clubs)
 * Images stored in /public/cards/
 */
const getCardImageUrl = (card: iCard): string => {
    // Map rank to image code
    const rankCode = card.rank === 1 ? 'A' : card.rank.toString();
    const suitCode = {
        spades: 'S',
        hearts: 'H',
        diamonds: 'D',
        clubs: 'C',
    }[card.suit];

    return `/cards/${rankCode}${suitCode}.png`;
};

const CardComponent: React.FC<iCardProps> = (props) => {
    const animating = props.animating ?? false;
    const disabled = props.disabled ?? false;
    const faceDown = props.faceDown ?? false;
    const highlighted = props.highlighted ?? false;
    const selected = props.selected ?? false;
    const small = props.small ?? false;

    const imageUrl = faceDown ? CARD_BACK_URL : getCardImageUrl(props.card);
    const color = getSuitColor(props.card.suit);

    const handleClick = () => {
        if (!disabled && props.onClick) {
            props.onClick();
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
                alt={faceDown ? 'Card back' : `${props.card.rank} of ${props.card.suit}`}
                className='card-image'
                draggable={false}
            />

            {selected && <div className='card-selection-indicator' />}

            {highlighted && <div className='card-highlight-indicator' />}
        </div>
    );
};

export default CardComponent;
