/**
 * Player's hand component
 */

import React from 'react';
import CardComponent from './Card';
import { Card } from '../types/Card';

interface HandProps {
    cards: Card[];
    isHuman: boolean;
    selectedCard: Card | null;
    onCardSelect?: (card: Card) => void;
    disabled?: boolean;
}

const Hand: React.FC<HandProps> = ({ cards, isHuman, selectedCard, onCardSelect, disabled = false }) => {
    return (
        <div className={`hand ${isHuman ? 'hand--human' : 'hand--npc'}`}>
            <div className='hand__cards'>
                {cards.map((card, index) => (
                    <div
                        key={card.id}
                        className='hand__card'
                        style={
                            {
                                '--card-index': index,
                                zIndex: index,
                            } as React.CSSProperties
                        }
                    >
                        <CardComponent
                            card={card}
                            faceDown={!isHuman}
                            selected={selectedCard?.id === card.id}
                            onClick={isHuman && onCardSelect ? () => onCardSelect(card) : undefined}
                            disabled={disabled || !isHuman}
                        />
                    </div>
                ))}
            </div>
            {!isHuman && <div className='hand__label'>NPC's Hand ({cards.length} cards)</div>}
            {isHuman && <div className='hand__label'>Your Hand</div>}
        </div>
    );
};

export default Hand;
