/**
 * Game over modal
 */

import React from 'react';

interface GameOverProps {
    winner: 'human' | 'npc';
    humanScore: number;
    npcScore: number;
    onPlayAgain: () => void;
    onMainMenu: () => void;
}

const GameOver: React.FC<GameOverProps> = ({ winner, humanScore, npcScore, onPlayAgain, onMainMenu }) => {
    const isWinner = winner === 'human';

    return (
        <div className='modal-overlay'>
            <div className={`modal game-over ${isWinner ? 'game-over--win' : 'game-over--lose'}`}>
                <div className='game-over-icon'>{isWinner ? '🎉' : '😔'}</div>
                <h2 className='game-over-title'>{isWinner ? 'Congratulations!' : 'Game Over'}</h2>
                <p className='game-over-message'>{isWinner ? 'You won the game!' : 'The NPC won this time.'}</p>
                <div className='game-over-scores'>
                    <div className={`game-over-score ${isWinner ? 'game-over-score--winner' : ''}`}>
                        <span className='game-over-score-label'>You</span>
                        <span className='game-over-score-value'>{humanScore}</span>
                    </div>
                    <div className='game-over-vs'>vs</div>
                    <div className={`game-over-score ${!isWinner ? 'game-over-score--winner' : ''}`}>
                        <span className='game-over-score-label'>NPC</span>
                        <span className='game-over-score-value'>{npcScore}</span>
                    </div>
                </div>
                <div className='game-over-actions'>
                    <button className='btn btn--primary' onClick={onPlayAgain}>
                        Play Again
                    </button>
                    <button className='btn btn--secondary' onClick={onMainMenu}>
                        Main Menu
                    </button>
                </div>
            </div>
        </div>
    );
};

export default GameOver;
