import { StatusCard } from './components/StatusCard';
import { useStatusPulse } from './hooks/useStatusPulse';
import './styles/status.scss';

function HeroTags({ name, pod, type }: { name: string; pod: number; type: string }) {
    return (
        <div className='hero__tags'>
            <span className='hero__tag'>{name}</span>
            <span className='hero__tag'>pod {pod}</span>
            <span className='hero__tag'>{type}</span>
        </div>
    );
}

export default function App() {
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
}
