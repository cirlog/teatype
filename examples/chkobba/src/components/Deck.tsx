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
            <div className='deck-stack'>
                {cardsRemaining > 0 ? (
                    <>
                        <img src='/cards/back.png' alt='Deck' className='deck-image' />
                        <div className='deck-shadow' />
                        <div className='deck-shadow deck-shadow--2' />
                    </>
                ) : (
                    <div className='deck-empty'>Empty</div>
                )}
            </div>
            <div className='deck-count'>{cardsRemaining} cards left</div>
        </div>
    );
};

export default Deck;
