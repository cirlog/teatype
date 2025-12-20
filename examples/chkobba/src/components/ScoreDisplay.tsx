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

// Types
import { iRoundScore } from '@/types/GameState';

interface iScoreDisplayProps {
    humanChkobbas: number;
    humanScore: number;
    npcChkobbas: number;
    npcScore: number;
    roundNumber: number;
    targetScore: number;
}

interface iRoundScoreModalProps {
    humanScore: iRoundScore;
    npcScore: iRoundScore;

    onContinue: () => void;
}

const ScoreDisplay: React.FC<iScoreDisplayProps> = (props) => {
    return (
        <div className='score-display'>
            <div className='score-display-round'>Round {props.roundNumber}</div>
            <div className='score-display-target'>First to {props.targetScore} wins</div>
            <div className='score-display-scores'>
                <div className='score-display-player'>
                    <div className='score-display-name'>You</div>
                    <div className='score-display-points'>{props.humanScore}</div>
                    {props.humanChkobbas > 0 && (
                        <div className='score-display-chkobbas'>
                            🎯 {props.humanChkobbas} Chkobba{props.humanChkobbas > 1 ? 's' : ''}
                        </div>
                    )}
                </div>
                <div className='score-display-divider'>vs</div>
                <div className='score-display-player'>
                    <div className='score-display-name'>NPC</div>
                    <div className='score-display-points'>{props.npcScore}</div>
                    {props.npcChkobbas > 0 && (
                        <div className='score-display-chkobbas'>
                            🎯 {props.npcChkobbas} Chkobba{props.npcChkobbas > 1 ? 's' : ''}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

const RoundScoreModal: React.FC<iRoundScoreModalProps> = (props) => {
    const categories = [
        { label: 'Cards (21+)', human: props.humanScore.cards, npc: props.npcScore.cards },
        { label: 'Diamonds ♦', human: props.humanScore.diamonds, npc: props.npcScore.diamonds },
        { label: '7♦ Sette di Deneri', human: props.humanScore.setteDeneri, npc: props.npcScore.setteDeneri },
        { label: 'Sevens (3+)', human: props.humanScore.sevens, npc: props.npcScore.sevens },
        { label: 'Chkobbas', human: props.humanScore.chkobbas, npc: props.npcScore.chkobbas },
    ];

    return (
        <div className='modal-overlay'>
            <div className='modal round-score-modal'>
                <h2>Round Complete!</h2>
                <table className='round-score-table'>
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>You</th>
                            <th>NPC</th>
                        </tr>
                    </thead>
                    <tbody>
                        {categories.map((cat) => (
                            <tr key={cat.label}>
                                <td>{cat.label}</td>
                                <td className={cat.human > 0 ? 'score-positive' : ''}>
                                    {cat.human > 0 ? `+${cat.human}` : '0'}
                                </td>
                                <td className={cat.npc > 0 ? 'score-positive' : ''}>
                                    {cat.npc > 0 ? `+${cat.npc}` : '0'}
                                </td>
                            </tr>
                        ))}
                        <tr className='round-score-total'>
                            <td>
                                <strong>Total</strong>
                            </td>
                            <td>
                                <strong>+{props.humanScore.total}</strong>
                            </td>
                            <td>
                                <strong>+{props.npcScore.total}</strong>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <button className='btn btn--primary' onClick={props.onContinue}>
                    Continue
                </button>
            </div>
        </div>
    );
};

export { RoundScoreModal };

export default ScoreDisplay;
