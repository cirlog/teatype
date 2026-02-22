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
import { ControlsPanel } from './tabs/ControlsPanel';
import { LogsPanel } from './tabs/LogsPanel';
import { StatusCard } from './tabs/StatusCard';
import { TeaSubNav, iTeaSubNavItem } from '../../../../../components';

// Context
import { DashboardProvider, useDashboard } from '../../context/DashboardContext';

// Hooks
import { useTranslation } from '../../../../../hooks';

// Icons
import { SettingsIcon, DatabaseIcon } from '../../../../../icons';

// Translations
import { translations } from '../../i18n';

// Style
import './style/ModuloDashboard.scss';

// Tab wrapper components that consume context
function StatusTabContent() {
    const { status, updating, error, refresh } = useDashboard();
    const { history } = useDashboard();
    const { t } = useTranslation(translations);
    return (
        <div id='controls'>
            <StatusCard status={status} updating={updating} error={error} onRefresh={refresh} />

            <section className='card card--timeline'>
                <h2>{t('dashboard.activity')}</h2>
                <ul>
                    {history.map((entry, idx) => (
                        <li key={`${entry}-${idx}`}>{entry}</li>
                    ))}
                </ul>
            </section>
        </div>
    );
}

function ControlsTabContent() {
    const { refresh } = useDashboard();
    return (
        <div id='status'>
            <ControlsPanel onActionComplete={refresh} />
            <LogsPanel maxHeight='500px' />
        </div>
    );
}

// Tab configuration with paths and components
const TABS: iTeaSubNavItem[] = [
    { id: 'status', label: 'Status', path: 'status', component: StatusTabContent, icon: <DatabaseIcon /> },
    { id: 'controls', label: 'Controls', path: 'controls', component: ControlsTabContent, icon: <SettingsIcon /> },
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

const ModuloDashboardApp = {
    title: 'Unit Dashboard',
    path: '/dashboard/*',
    content: ModuloDashboard,
    longDescription: 'Monitor and control your Modulo application with live status, logs, and command execution.',
    shortDescription: 'Operations Pulse Dashboard',
    icon: <SettingsIcon />,
    tags: ['Admin', 'Modulo'],
};

export default ModuloDashboard;

export { ModuloDashboardApp };
