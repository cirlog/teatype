/**
 * Deck component showing remaining cards
 */

import React from 'react';

interface DeckProps {
    cardsRemaining: number;
}

const Deck: React.FC<DeckProps> = ({ cardsRemaining }) => {
    return (
        <div className='deck'>
            <div className='deck__stack'>
                {cardsRemaining > 0 ? (
                    <>
                        <img src='/cards/back.png' alt='Deck' className='deck__image' />
                        <div className='deck__shadow' />
                        <div className='deck__shadow deck__shadow--2' />
                    </>
                ) : (
                    <div className='deck__empty'>Empty</div>
                )}
            </div>
            <div className='deck__count'>{cardsRemaining} cards left</div>
        </div>
    );
};

export default Deck;
