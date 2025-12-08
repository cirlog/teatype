import type { StatusSnapshot } from '../hooks/useStatusPulse';

interface StatusCardProps {
    status: StatusSnapshot;
    updating: boolean;
    error: string | null;
    onRefresh: () => void;
}

export function StatusCard({ status, updating, error, onRefresh }: StatusCardProps) {
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
            <button className='refresh-btn' data-refresh onClick={onRefresh} disabled={updating}>
                {updating ? 'Syncing …' : 'Status pulse'}
            </button>
        </section>
    );
}
