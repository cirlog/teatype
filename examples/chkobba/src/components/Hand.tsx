/**
 * iPlayer's hand component
 */

import React from 'react';
import CardComponent from './Card';
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
