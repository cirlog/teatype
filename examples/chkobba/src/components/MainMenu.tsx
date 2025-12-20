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
import { tDifficulty } from '../types/GameState';

interface iMainMenuProps {
    difficulty: tDifficulty;
    targetScore: number;
    trainingMode: boolean;
    onDifficultyChange: (difficulty: tDifficulty) => void;
    onTargetScoreChange: (score: number) => void;
    onTrainingModeChange: (enabled: boolean) => void;
    onStartGame: () => void;
}

const MainMenu: React.FC<iMainMenuProps> = ({
    difficulty,
    targetScore,
    trainingMode,
    onDifficultyChange,
    onTargetScoreChange,
    onTrainingModeChange,
    onStartGame,
}) => {
    const difficulties: { value: tDifficulty; label: string; description: string }[] = [
        { value: 'easy', label: 'Noob', description: 'Random moves, forgiving play' },
        { value: 'medium', label: 'Casual', description: 'Basic strategy, occasional mistakes' },
        { value: 'hard', label: 'Expert', description: 'Strong strategy, few mistakes' },
        { value: 'expert', label: 'Yessmine🌼', description: 'Optimal play, card counting. You will suffer' },
    ];

    const scoreOptions = [7, 11, 15, 21];

    return (
        <div className='main-menu'>
            <div className='main-menu-header'>
                <h1 className='main-menu-title'>🃏Chkobba</h1>
                <p className='main-menu-subtitle'>لعبة ورق تونسية</p>
            </div>

            <div className='main-menu-options'>
                <div className='option-group'>
                    <label className='option-label'>Difficulty-Level:</label>
                    <div className='difficulty-selector'>
                        {difficulties.map((d) => (
                            <button
                                key={d.value}
                                className={`difficulty-btn ${difficulty === d.value ? 'difficulty-btn--active' : ''}`}
                                onClick={() => onDifficultyChange(d.value)}
                            >
                                <span className='difficulty-btn-label'>{d.label}</span>
                                <span className='difficulty-btn-desc'>{d.description}</span>
                            </button>
                        ))}
                    </div>
                </div>

                <div className='option-group'>
                    <label className='option-label'>Target Score:</label>
                    <div className='score-selector'>
                        {scoreOptions.map((score) => (
                            <button
                                key={score}
                                className={`score-btn ${targetScore === score ? 'score-btn--active' : ''}`}
                                onClick={() => onTargetScoreChange(score)}
                            >
                                {score}
                            </button>
                        ))}
                    </div>
                </div>

                <div className='option-group'>
                    <label className='option-label'>Training Mode:</label>
                    <button
                        className={`training-toggle ${trainingMode ? 'training-toggle--active' : ''}`}
                        onClick={() => onTrainingModeChange(!trainingMode)}
                    >
                        <span className='training-toggle-icon'>{trainingMode ? '💡' : '🎓'}</span>
                        <div className='training-toggle-content'>
                            <span className='training-toggle-label'>
                                {trainingMode ? 'Training Mode ON' : 'Training Mode OFF'}
                            </span>
                            <span className='training-toggle-desc'>
                                {trainingMode
                                    ? 'Tips and best moves will be shown during gameplay'
                                    : 'Enable to see strategic tips during the game'}
                            </span>
                        </div>
                        <span className='training-toggle-switch'>
                            <span className='training-toggle-switch-knob' />
                        </span>
                    </button>
                </div>
            </div>

            <button className='btn btn--primary btn--large' onClick={onStartGame}>
                Start Game
            </button>

            <div className='main-menu-rules'>
                <h3>Quick Rules</h3>
                <ul>
                    <li>
                        <strong>Deck:</strong> 40 cards (A-10, no J/Q/K)
                    </li>
                    <li>
                        <strong>Picture cards (8-10):</strong> Take ALL table cards, no Chkobba
                    </li>
                    <li>
                        <strong>Number cards (1-7):</strong> Capture cards that sum to your card's value
                    </li>
                    <li>
                        <strong>Chkobba:</strong> Clear the table with a 2-7 card = +1 point
                    </li>
                    <li>
                        <strong>Ace:</strong> Can capture (value 1) but cannot make Chkobba
                    </li>
                </ul>
                <h4>Scoring</h4>
                <ul>
                    <li>Most cards (21+): +1 point</li>
                    <li>Most diamonds: +1 point</li>
                    <li>7♦ (Sette di Deneri): +1 point</li>
                    <li>Most 7s (3+): +1 point</li>
                    <li>Each Chkobba: +1 point</li>
                </ul>
            </div>
        </div>
    );
};

export default MainMenu;
