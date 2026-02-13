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

import { useState } from 'react';

// Teatype components
import { TeaButton, TeaInput } from '../../../../components';

import { useAppCommands } from '../hooks/useAppCommands';

import './style/ControlsPanel.scss';

interface iControlsPanelProps {
    onActionComplete?: () => void;
}

export function ControlsPanel({ onActionComplete }: iControlsPanelProps) {
    const { sendCommand, stopApp, rebootApp, loading, error, lastResult } = useAppCommands();
    const [commandInput, setCommandInput] = useState('');
    const [showConfirm, setShowConfirm] = useState<'stop' | 'reboot' | null>(null);

    const handleStop = async () => {
        if (showConfirm === 'stop') {
            await stopApp();
            setShowConfirm(null);
            onActionComplete?.();
        } else {
            setShowConfirm('stop');
        }
    };

    const handleReboot = async () => {
        if (showConfirm === 'reboot') {
            await rebootApp();
            setShowConfirm(null);
            onActionComplete?.();
        } else {
            setShowConfirm('reboot');
        }
    };

    const handleCommandSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!commandInput.trim()) return;

        // Parse command - format: "command:arg1,arg2" or just "command"
        const [command, argsStr] = commandInput.split(':');
        let payload: Record<string, any> = {};

        if (argsStr) {
            // Try to parse as JSON first
            try {
                payload = JSON.parse(argsStr);
            } catch {
                // Otherwise treat as simple key-value pairs
                argsStr.split(',').forEach((arg, i) => {
                    const [key, value] = arg.split('=');
                    payload[key || `arg${i}`] = value || true;
                });
            }
        }

        await sendCommand(command.trim(), payload);
        setCommandInput('');
        onActionComplete?.();
    };

    const cancelConfirm = () => setShowConfirm(null);

    return (
        <section className='card controls-panel'>
            <h2>Application Controls</h2>

            <div className='controls-panel__buttons'>
                <TeaButton
                    disabled={loading}
                    onClick={handleStop}
                    variant={showConfirm === 'stop' ? 'danger' : 'danger'}
                >
                    {showConfirm === 'stop' ? '⚠️ Confirm Stop' : '⏹️ Stop'}
                </TeaButton>

                <TeaButton variant='secondary' onClick={handleReboot} disabled={loading}>
                    {showConfirm === 'reboot' ? '⚠️ Confirm Reboot' : '🔄 Reboot'}
                </TeaButton>

                {showConfirm && (
                    <TeaButton variant='ghost' onClick={cancelConfirm}>
                        Cancel
                    </TeaButton>
                )}
            </div>

            <form className='controls-panel__command-form' onSubmit={handleCommandSubmit}>
                <div className='command-input-wrapper'>
                    <span className='command-prompt'>$</span>
                    <TeaInput
                        placeholder='Enter command (e.g., ping, status, custom_cmd:{"key":"value"})'
                        value={commandInput}
                        onChange={(e) => setCommandInput(e.target.value)}
                        disabled={loading}
                    />
                    <TeaButton type='submit' variant='primary' size='sm' disabled={loading || !commandInput.trim()}>
                        {loading ? '...' : '▶'}
                    </TeaButton>
                </div>
            </form>

            {error && <div className='controls-panel__error'>❌ {error}</div>}

            {lastResult && (
                <div className={`controls-panel__result ${lastResult.success ? 'success' : 'error'}`}>
                    <pre>{JSON.stringify(lastResult, null, 2)}</pre>
                </div>
            )}
        </section>
    );
}

export default ControlsPanel;
