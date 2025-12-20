/**
 * Card component with local PNG images
 */

import React from 'react';
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
