/**
 * Main App component for Chkobba
 */

import React from 'react';
import MainMenu from './components/MainMenu';
import GameBoard from './components/GameBoard';
import { RoundScoreModal } from './components/ScoreDisplay';
import GameOver from './components/GameOver';
import { useGameState } from './hooks/useGameState';

const App: React.FC = () => {
    const {
        state,
        roundScores,
        trainingTip,
        setDifficulty,
        setTargetScore,
        setTrainingMode,
        handleStartGame,
        handleContinueRound,
        handlePlayAgain,
        handleMainMenu,
        handleCardSelect,
        handleTableCardSelect,
        handleConfirmCapture,
        handleCancelSelection,
    } = useGameState();

    return (
        <div className='app'>
            {state.phase === 'menu' && (
                <MainMenu
                    difficulty={state.difficulty}
                    targetScore={state.targetScore}
                    trainingMode={state.trainingMode}
                    onDifficultyChange={setDifficulty}
                    onTargetScoreChange={setTargetScore}
                    onTrainingModeChange={setTrainingMode}
                    onStartGame={handleStartGame}
                />
            )}

            {state.phase === 'playing' && (
                <GameBoard
                    state={state}
                    trainingTip={trainingTip}
                    onCardSelect={handleCardSelect}
                    onTableCardSelect={handleTableCardSelect}
                    onConfirmCapture={handleConfirmCapture}
                    onCancelSelection={handleCancelSelection}
                />
            )}

            {state.phase === 'roundEnd' && roundScores && (
                <>
                    <GameBoard
                        state={state}
                        trainingTip={null}
                        onCardSelect={() => {}}
                        onTableCardSelect={() => {}}
                        onConfirmCapture={() => {}}
                        onCancelSelection={() => {}}
                    />
                    <RoundScoreModal
                        humanScore={roundScores.human}
                        npcScore={roundScores.npc}
                        onContinue={handleContinueRound}
                    />
                </>
            )}

            {state.phase === 'gameEnd' && (
                <>
                    <GameBoard
                        state={state}
                        trainingTip={null}
                        onCardSelect={() => {}}
                        onTableCardSelect={() => {}}
                        onConfirmCapture={() => {}}
                        onCancelSelection={() => {}}
                    />
                    <GameOver
                        winner={state.humanTotalScore >= state.targetScore ? 'human' : 'npc'}
                        humanScore={state.humanTotalScore}
                        npcScore={state.npcTotalScore}
                        onPlayAgain={handlePlayAgain}
                        onMainMenu={handleMainMenu}
                    />
                </>
            )}
        </div>
    );
};

export default App;
