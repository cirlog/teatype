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

// Components
import { ControlsPanel } from './ControlsPanel';
import { LogsPanel } from './LogsPanel';
import { StatusCard } from './StatusCard';

// Hooks
import useStatusPulse from '../hooks/useStatusPulse';

// Style
import './style/ModuloDashboard.scss';

const ModuloDashboard = () => {
    const { status, history, updating, error, refresh } = useStatusPulse();

    return (
        <div id='modulo-dashboard'>
            {/* Top row - Status and Controls */}
            <div className='row'>
                <StatusCard status={status} updating={updating} error={error} onRefresh={refresh} />
                <ControlsPanel onActionComplete={refresh} />
            </div>

            {/* Activity timeline */}
            <section className='card card--timeline'>
                <h2>Activity</h2>
                <ul>
                    {history.map((entry, idx) => (
                        <li key={`${entry}-${idx}`}>{entry}</li>
                    ))}
                </ul>
            </section>

            {/* Full-width logs panel */}
            <LogsPanel maxHeight='350px' />
        </div>
    );
};

export default ModuloDashboard;
