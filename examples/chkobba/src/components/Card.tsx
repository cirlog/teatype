/**
 * Card component with local PNG images
 */

import React from 'react';
import { Card as CardType, getSuitColor } from '../types/Card';

interface CardProps {
    card: CardType;
    faceDown?: boolean;
    selected?: boolean;
    highlighted?: boolean;
    onClick?: () => void;
    disabled?: boolean;
    small?: boolean;
}

/**
 * Get local card image URL
 * Card codes: A, 2-9, 0 (for 10) + S (spades), H (hearts), D (diamonds), C (clubs)
 * Images stored in /public/cards/
 */
function getCardImageUrl(card: CardType): string {
    // deckofcardsapi uses '0' for 10, 'A' for Ace
    const rankCode = card.rank === 1 ? 'A' : card.rank === 10 ? '0' : card.rank.toString();
    const suitCode = {
        spades: 'S',
        hearts: 'H',
        diamonds: 'D',
        clubs: 'C',
    }[card.suit];

    return `/cards/${rankCode}${suitCode}.png`;
}

const CARD_BACK_URL = '/cards/back.png';

const CardComponent: React.FC<CardProps> = ({
    card,
    faceDown = false,
    selected = false,
    highlighted = false,
    onClick,
    disabled = false,
    small = false,
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
    ]
        .filter(Boolean)
        .join(' ');

    return (
        <div className={cardClass} onClick={handleClick}>
            <img
                src={imageUrl}
                alt={faceDown ? 'Card back' : `${card.rank} of ${card.suit}`}
                className='card__image'
                draggable={false}
            />
            {selected && <div className='card__selection-indicator' />}
            {highlighted && <div className='card__highlight-indicator' />}
        </div>
    );
};

export default CardComponent;
