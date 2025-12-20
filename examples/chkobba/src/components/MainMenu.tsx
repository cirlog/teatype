/**
 * Main menu component
 */

import React from 'react';
import { Difficulty } from '../types/GameState';
import { getRandomStrategyTip } from '../game/TrainingTips';

interface MainMenuProps {
    difficulty: Difficulty;
    targetScore: number;
    trainingMode: boolean;
    onDifficultyChange: (difficulty: Difficulty) => void;
    onTargetScoreChange: (score: number) => void;
    onTrainingModeChange: (enabled: boolean) => void;
    onStartGame: () => void;
}

const MainMenu: React.FC<MainMenuProps> = ({
    difficulty,
    targetScore,
    trainingMode,
    onDifficultyChange,
    onTargetScoreChange,
    onTrainingModeChange,
    onStartGame,
}) => {
    const difficulties: { value: Difficulty; label: string; description: string }[] = [
        { value: 'easy', label: 'Easy', description: 'Random moves, forgiving play' },
        { value: 'medium', label: 'Medium', description: 'Basic strategy, occasional mistakes' },
        { value: 'hard', label: 'Hard', description: 'Strong strategy, few mistakes' },
        { value: 'expert', label: 'Expert', description: 'Optimal play, card counting' },
    ];

    const scoreOptions = [7, 11, 15, 21];
    const [strategyTip] = React.useState(() => getRandomStrategyTip());

    return (
        <div className='main-menu'>
            <div className='main-menu__header'>
                <h1 className='main-menu__title'>🃏 Chkobba</h1>
                <p className='main-menu__subtitle'>Tunisian Card Game</p>
            </div>

            <div className='main-menu__options'>
                <div className='option-group'>
                    <label className='option-label'>Difficulty</label>
                    <div className='difficulty-selector'>
                        {difficulties.map((d) => (
                            <button
                                key={d.value}
                                className={`difficulty-btn ${difficulty === d.value ? 'difficulty-btn--active' : ''}`}
                                onClick={() => onDifficultyChange(d.value)}
                            >
                                <span className='difficulty-btn__label'>{d.label}</span>
                                <span className='difficulty-btn__desc'>{d.description}</span>
                            </button>
                        ))}
                    </div>
                </div>

                <div className='option-group'>
                    <label className='option-label'>Target Score</label>
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
                    <label className='option-label'>Training Mode</label>
                    <button
                        className={`training-toggle ${trainingMode ? 'training-toggle--active' : ''}`}
                        onClick={() => onTrainingModeChange(!trainingMode)}
                    >
                        <span className='training-toggle__icon'>{trainingMode ? '💡' : '🎓'}</span>
                        <div className='training-toggle__content'>
                            <span className='training-toggle__label'>
                                {trainingMode ? 'Training Mode ON' : 'Training Mode OFF'}
                            </span>
                            <span className='training-toggle__desc'>
                                {trainingMode
                                    ? 'Tips and best moves will be shown during gameplay'
                                    : 'Enable to see strategic tips during the game'}
                            </span>
                        </div>
                        <span className='training-toggle__switch'>
                            <span className='training-toggle__switch-knob' />
                        </span>
                    </button>
                </div>
            </div>

            <button className='btn btn--primary btn--large' onClick={onStartGame}>
                Start Game
            </button>

            {/* Strategy tip of the day */}
            <div className='main-menu__tip'>
                <div className='strategy-tip'>
                    <span className='strategy-tip__badge'>💡 Strategy Tip</span>
                    <h4 className='strategy-tip__title'>{strategyTip.title}</h4>
                    <p className='strategy-tip__message'>{strategyTip.message}</p>
                </div>
            </div>

            <div className='main-menu__rules'>
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
