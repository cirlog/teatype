/**
 * Capture selector for when multiple captures are possible
 */

import React from 'react';
import CardComponent from './Card';
import { Card } from '../types/Card';

interface CaptureSelectorProps {
    playedCard: Card;
    captures: Card[][];
    onSelect: (capture: Card[]) => void;
    onCancel: () => void;
}

const CaptureSelector: React.FC<CaptureSelectorProps> = ({ playedCard, captures, onSelect, onCancel }) => {
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
                            <div className='capture-option__cards'>
                                {capture.map((card) => (
                                    <CardComponent key={card.id} card={card} small />
                                ))}
                            </div>
                            <div className='capture-option__sum'>Sum: {capture.reduce((s, c) => s + c.value, 0)}</div>
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
