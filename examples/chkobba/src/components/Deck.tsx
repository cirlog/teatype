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
