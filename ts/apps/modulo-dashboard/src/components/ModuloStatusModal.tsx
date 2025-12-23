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
import { StatusCard } from '@/components/StatusCard';

// Hooks
import { useStatusPulse } from '@/hooks/useStatusPulse';

// Style
import '@/components/style/ModuloStatusModal.scss';

const HeroTags = ({ name, pod, type }: { name: string; pod: number; type: string }) => {
    return (
        <div className='hero__tags'>
            <span className='hero__tag'>{name}</span>
            <span className='hero__tag'>pod {pod}</span>
            <span className='hero__tag'>{type}</span>
        </div>
    );
};

const ModuloStatusModal = () => {
    const { status, history, updating, error, refresh } = useStatusPulse();

    return (
        <div className='page'>
            <header className='hero'>
                <div className='hero__content'>
                    <p className='hero__eyebrow'>Realtime module vitals</p>
                    <h1>Operations Pulse</h1>
                    <p className='hero__lede'>
                        A lightweight dashboard pinging the backend status endpoint. Rebuilt in React + Vite for faster
                        iteration.
                    </p>
                    <HeroTags name={status.unit} pod={0} type={status.type} />
                </div>
            </header>

            <main className='grid'>
                <StatusCard status={status} updating={updating} error={error} onRefresh={refresh} />
                <section className='card card--timeline'>
                    <h2>Activity</h2>
                    <ul>
                        {history.map((entry, idx) => (
                            <li key={`${entry}-${idx}`}>{entry}</li>
                        ))}
                    </ul>
                </section>
            </main>
        </div>
    );
};

export default ModuloStatusModal;
