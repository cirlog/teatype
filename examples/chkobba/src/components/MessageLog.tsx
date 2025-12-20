/**
 * Message log component showing game action history
 */

import React, { useEffect, useRef } from 'react';
import { iGameAction } from '../types/GameState';

interface iMessageLogProps {
    actions: iGameAction[];
    maxVisible?: number;
}

const MessageLog: React.FC<iMessageLogProps> = ({ actions, maxVisible = 15 }) => {
    const logRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        if (logRef.current) {
            logRef.current.scrollTop = logRef.current.scrollHeight;
        }
    }, [actions.length]);

    const visibleActions = actions.slice(-maxVisible);
    const totalActions = actions.length;

    const getActionIcon = (action: iGameAction): string => {
        switch (action.type) {
            case 'chkobba':
                return '🎯';
            case 'capture':
                return '✋';
            case 'drop':
                return '📤';
            case 'deal':
                return '🎴';
            case 'info':
            default:
                return 'ℹ️';
        }
    };

    const getActionClass = (action: iGameAction, index: number): string => {
        const isLatest = index === visibleActions.length - 1;
        const fadeLevel = Math.max(0, visibleActions.length - 1 - index);

        let className = 'message-log-item';
        className += ` message-log-item--${action.type}`;
        className += ` message-log-item--${action.player}`;

        if (isLatest) {
            className += ' message-log-item--latest';
        } else if (fadeLevel > 0) {
            className += ` message-log-item--fade-${Math.min(fadeLevel, 5)}`;
        }

        return className;
    };

    return (
        <div className='message-log'>
            <div className='message-log-header'>
                <span className='message-log-title'>📜 Game Log</span>
                <span className='message-log-count'>{totalActions} actions</span>
            </div>
            <div className='message-log-content' ref={logRef}>
                {visibleActions.length === 0 ? (
                    <div className='message-log-empty'>No actions yet...</div>
                ) : (
                    visibleActions.map((action, index) => (
                        <div key={action.id} className={getActionClass(action, index)}>
                            <span className='message-log-icon'>{getActionIcon(action)}</span>
                            <span className='message-log-text'>{action.message}</span>
                        </div>
                    ))
                )}
            </div>
            {totalActions > maxVisible && <div className='message-log-fade-top' />}
        </div>
    );
};

export default MessageLog;
