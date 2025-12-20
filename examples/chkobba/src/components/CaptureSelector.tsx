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

// Components
import CardComponent from './Card';

// Types
import { iCard } from '../types/Card';

interface iCaptureSelectorProps {
    playedCard: iCard;
    captures: iCard[][];
    onSelect: (capture: iCard[]) => void;
    onCancel: () => void;
}

const CaptureSelector: React.FC<iCaptureSelectorProps> = ({ playedCard, captures, onSelect, onCancel }) => {
    return (
        <div className='modal-overlay'>
            <div className='modal capture-selector'>
                <h3>Select cards to capture</h3>
                <p>
                    Your card: <strong>{playedCard.rank}</strong> (value: {playedCard.value})
                </p>
                <div className='capture-options'>
                    {captures.map((capture, index) => (
                        <div key={index} className='capture-option' onClick={() => onSelect(capture)}>
                            <div className='capture-option-cards'>
                                {capture.map((card) => (
                                    <CardComponent key={card.id} card={card} small />
                                ))}
                            </div>
                            <div className='capture-option-sum'>Sum: {capture.reduce((s, c) => s + c.value, 0)}</div>
                        </div>
                    ))}
                </div>
                <button className='btn btn--secondary' onClick={onCancel}>
                    Cancel
                </button>
            </div>
        </div>
    );
};

export default CaptureSelector;
