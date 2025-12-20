/**
 * Score display component
 */

import React from 'react';
import { RoundScore } from '../types/GameState';

interface ScoreDisplayProps {
    humanScore: number;
    npcScore: number;
    humanChkobbas: number;
    npcChkobbas: number;
    targetScore: number;
    roundNumber: number;
}

const ScoreDisplay: React.FC<ScoreDisplayProps> = ({
    humanScore,
    npcScore,
    humanChkobbas,
    npcChkobbas,
    targetScore,
    roundNumber,
}) => {
    return (
        <div className='score-display'>
            <div className='score-display__round'>Round {roundNumber}</div>
            <div className='score-display__target'>First to {targetScore} wins</div>
            <div className='score-display__scores'>
                <div className='score-display__player'>
                    <div className='score-display__name'>You</div>
                    <div className='score-display__points'>{humanScore}</div>
                    {humanChkobbas > 0 && (
                        <div className='score-display__chkobbas'>
                            🎯 {humanChkobbas} Chkobba{humanChkobbas > 1 ? 's' : ''}
                        </div>
                    )}
                </div>
                <div className='score-display__divider'>vs</div>
                <div className='score-display__player'>
                    <div className='score-display__name'>NPC</div>
                    <div className='score-display__points'>{npcScore}</div>
                    {npcChkobbas > 0 && (
                        <div className='score-display__chkobbas'>
                            🎯 {npcChkobbas} Chkobba{npcChkobbas > 1 ? 's' : ''}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

interface RoundScoreModalProps {
    humanScore: RoundScore;
    npcScore: RoundScore;
    onContinue: () => void;
}

export const RoundScoreModal: React.FC<RoundScoreModalProps> = ({ humanScore, npcScore, onContinue }) => {
    const categories = [
        { label: 'Cards (21+)', human: humanScore.cards, npc: npcScore.cards },
        { label: 'Diamonds ♦', human: humanScore.diamonds, npc: npcScore.diamonds },
        { label: '7♦ Sette di Deneri', human: humanScore.setteDeneri, npc: npcScore.setteDeneri },
        { label: 'Sevens (3+)', human: humanScore.sevens, npc: npcScore.sevens },
        { label: 'Chkobbas', human: humanScore.chkobbas, npc: npcScore.chkobbas },
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
                                <strong>+{humanScore.total}</strong>
                            </td>
                            <td>
                                <strong>+{npcScore.total}</strong>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <button className='btn btn--primary' onClick={onContinue}>
                    Continue
                </button>
            </div>
        </div>
    );
};

export default ScoreDisplay;
