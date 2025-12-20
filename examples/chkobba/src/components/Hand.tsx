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
    animatingCardId?: string;
}

const Hand: React.FC<HandProps> = ({
    cards,
    isHuman,
    selectedCard,
    onCardSelect,
    disabled = false,
    animatingCardId,
}) => {
    return (
        <div className={`hand ${isHuman ? 'hand--human' : 'hand--npc'}`}>
            <div className='hand__cards'>
                {cards.map((card, index) => (
                    <div
                        key={card.id}
                        className={`hand__card ${animatingCardId === card.id ? 'hand__card--animating' : ''}`}
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
                            animating={animatingCardId === card.id}
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
