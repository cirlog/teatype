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
                <div className='game-over__icon'>{isWinner ? '🎉' : '😔'}</div>
                <h2 className='game-over__title'>{isWinner ? 'Congratulations!' : 'Game Over'}</h2>
                <p className='game-over__message'>{isWinner ? 'You won the game!' : 'The NPC won this time.'}</p>
                <div className='game-over__scores'>
                    <div className={`game-over__score ${isWinner ? 'game-over__score--winner' : ''}`}>
                        <span className='game-over__score-label'>You</span>
                        <span className='game-over__score-value'>{humanScore}</span>
                    </div>
                    <div className='game-over__vs'>vs</div>
                    <div className={`game-over__score ${!isWinner ? 'game-over__score--winner' : ''}`}>
                        <span className='game-over__score-label'>NPC</span>
                        <span className='game-over__score-value'>{npcScore}</span>
                    </div>
                </div>
                <div className='game-over__actions'>
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
