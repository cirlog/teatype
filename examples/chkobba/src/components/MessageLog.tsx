/**
 * Message log component showing game action history
 */

import React, { useEffect, useRef } from 'react';
import { GameAction } from '../types/GameState';

interface MessageLogProps {
    actions: GameAction[];
    maxVisible?: number;
}

const MessageLog: React.FC<MessageLogProps> = ({ actions, maxVisible = 15 }) => {
    const logRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        if (logRef.current) {
            logRef.current.scrollTop = logRef.current.scrollHeight;
        }
    }, [actions.length]);

    const visibleActions = actions.slice(-maxVisible);
    const totalActions = actions.length;

    const getActionIcon = (action: GameAction): string => {
        switch (action.type) {
            case 'chkobba':
                return '🎯';
            case 'capture':
                return '✋';
            case 'picture-capture':
                return '🃏';
            case 'drop':
                return '📤';
            case 'deal':
                return '🎴';
            case 'info':
            default:
                return 'ℹ️';
        }
    };

    const getActionClass = (action: GameAction, index: number): string => {
        const isLatest = index === visibleActions.length - 1;
        const fadeLevel = Math.max(0, visibleActions.length - 1 - index);

        let className = 'message-log__item';
        className += ` message-log__item--${action.type}`;
        className += ` message-log__item--${action.player}`;

        if (isLatest) {
            className += ' message-log__item--latest';
        } else if (fadeLevel > 0) {
            className += ` message-log__item--fade-${Math.min(fadeLevel, 5)}`;
        }

        return className;
    };

    return (
        <div className='message-log'>
            <div className='message-log__header'>
                <span className='message-log__title'>📜 Game Log</span>
                <span className='message-log__count'>{totalActions} actions</span>
            </div>
            <div className='message-log__content' ref={logRef}>
                {visibleActions.length === 0 ? (
                    <div className='message-log__empty'>No actions yet...</div>
                ) : (
                    visibleActions.map((action, index) => (
                        <div key={action.id} className={getActionClass(action, index)}>
                            <span className='message-log__icon'>{getActionIcon(action)}</span>
                            <span className='message-log__text'>{action.message}</span>
                        </div>
                    ))
                )}
            </div>
            {totalActions > maxVisible && <div className='message-log__fade-top' />}
        </div>
    );
};

export default MessageLog;
