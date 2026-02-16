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
import { TeaSubNav, iTeaSubNavItem } from '../../../../components';

// Context
import { DashboardProvider, useDashboard } from '../context/DashboardContext';

// Hooks
import { useTranslation } from '../../../../hooks';

// Icons
import { RoundedSquareIcon, SettingsIcon, DatabaseIcon, ArrowIcon } from '../../../../icons';

// Translations
import { translations } from '../i18n';

// Style
import './style/ModuloDashboard.scss';

// Tab wrapper components that consume context
function StatusTabContent() {
    const { status, updating, error, refresh } = useDashboard();
    return <StatusCard status={status} updating={updating} error={error} onRefresh={refresh} />;
}

function ControlsTabContent() {
    const { refresh } = useDashboard();
    return <ControlsPanel onActionComplete={refresh} />;
}

function LogsTabContent() {
    return <LogsPanel maxHeight='500px' />;
}

function ActivityTabContent() {
    const { history } = useDashboard();
    const { t } = useTranslation(translations);

    return (
        <section className='card card--timeline'>
            <h2>{t('dashboard.activity')}</h2>
            <ul>
                {history.map((entry, idx) => (
                    <li key={`${entry}-${idx}`}>{entry}</li>
                ))}
            </ul>
        </section>
    );
}

// Tab configuration with paths and components
const TABS: iTeaSubNavItem[] = [
    { id: 'status', label: 'Status', path: 'status', component: StatusTabContent, icon: <RoundedSquareIcon /> },
    { id: 'controls', label: 'Controls', path: 'controls', component: ControlsTabContent, icon: <SettingsIcon /> },
    { id: 'logs', label: 'Logs', path: 'logs', component: LogsTabContent, icon: <DatabaseIcon /> },
    { id: 'activity', label: 'Activity', path: 'activity', component: ActivityTabContent, icon: <ArrowIcon /> },
];

const ModuloDashboard = () => {
    return (
        <DashboardProvider>
            <div id='modulo-dashboard'>
                <TeaSubNav items={TABS} basePath='/dashboard' />
            </div>
        </DashboardProvider>
    );
};

export default ModuloDashboard;
