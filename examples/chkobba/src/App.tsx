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
import GameBoard from './components/GameBoard';
import GameOver from './components/GameOver';
import MainMenu from './components/MainMenu';
import { RoundScoreModal } from './components/ScoreDisplay';

// Hooks
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
