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

// Teatype components
import { TeaButton } from '../../../../../../components';

import type { tStatusSnapshot } from '../../../hooks/useStatusPulse';

interface iStatusCardProps {
    error: string | null;
    status: tStatusSnapshot;
    updating: boolean;

    onRefresh: () => void;
}

export function StatusCard({ status, updating, error, onRefresh }: iStatusCardProps) {
    const pillLabel = updating ? 'Updating' : error ? 'Offline' : 'Online';
    const pillStyle = {
        background: error ? 'rgba(249, 115, 22, 0.18)' : 'rgba(16, 185, 129, 0.18)',
        color: error ? '#f97316' : '#10b981',
    };

    return (
        <section className='card' data-status-card>
            <div className='status-header'>
                <h2>Live Status</h2>
                <span className='status-pill' style={pillStyle} data-status-pill>
                    {pillLabel}
                </span>
            </div>
            <div className='status-body'>
                <dl>
                    <div>
                        <dt>Designation</dt>
                        <dd>{status.designation}</dd>
                    </div>
                    <div>
                        <dt>Uptime loops</dt>
                        <dd>{status.loop_iter.toLocaleString()}</dd>
                    </div>
                    <div>
                        <dt>Signal</dt>
                        <dd>{status.status}</dd>
                    </div>
                    <div>
                        <dt>Unit</dt>
                        <dd>{status.unit}</dd>
                    </div>
                </dl>
            </div>
            <TeaButton variant='primary' onClick={onRefresh} disabled={updating} loading={updating}>
                {updating ? 'Syncing …' : 'Status pulse'}
            </TeaButton>
        </section>
    );
}
