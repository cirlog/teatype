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
import React, { useEffect, useRef } from 'react';

// Types
import { iGameAction } from '@/types/GameState';

interface iMessageLogProps {
    actions: iGameAction[];
    maxVisible?: number;
}

const MessageLog: React.FC<iMessageLogProps> = (props) => {
    const logRef = useRef<HTMLDivElement>(null);

    const maxVisible = props.maxVisible ?? 15;

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        if (logRef.current) {
            logRef.current.scrollTop = logRef.current.scrollHeight;
        }
    }, [props.actions.length]);

    const visibleActions = props.actions.slice(-maxVisible);
    const totalActions = props.actions.length;

    const getActionIcon = (action: iGameAction): string => {
        switch (action.type) {
            case 'chkobba':
                return '🎯';
            case 'capture':
                return '✋';
            case 'drop':
                return '👇';
            case 'deal':
                return '🎲';
            case 'info':
                return 'ℹ️';
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
