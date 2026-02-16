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

/**
 * Modulo Dashboard - Standalone entry point and re-exports.
 *
 * This file serves as both:
 * 1. The standalone app entry point (renders to DOM)
 * 2. The module entry point for importing ModuloDashboard in other apps
 */

// React imports
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

// Components
import { iPageInfo, TeaApp } from '../../../components';
import ClientKit from './components/ClientKit';
import ModuloDashboard from './components/ModuloDashboard';

// Utility
import { Store } from '../../../toolkit';

// Icons
import { ModelsIcon, SettingsIcon } from '../../../icons';

const APP_NAME = 'Modulo';
const SUBTITLE = 'Lightweight dashboard for monitoring and controlling Modulo Units';

// Set to true to enable development features like React DevTools integration and verbose logging
const DEV_MODE = true;
Store.memory.set('devMode', DEV_MODE);

const PAGES: iPageInfo[] = [
    {
        title: 'Unit Dashboard',
        path: '/dashboard/*',
        content: ModuloDashboard,
        longDescription: 'Monitor and control your Modulo application with live status, logs, and command execution.',
        shortDescription: 'Operations Pulse Dashboard',
        icon: <SettingsIcon />,
        tags: ['Admin', 'Modulo'],
    },
];
if (DEV_MODE) {
    PAGES.push({
        title: 'Client-Kit',
        path: '/client-kit',
        content: ClientKit,
        longDescription: 'A playground for testing and showcasing client-side components and interactions.',
        shortDescription: 'Client-side Component Kit',
        icon: <ModelsIcon />,
        tags: ['Dev', 'Test'],
    });
}

/**
 * StandaloneModuloDashboard - Entry point for standalone Modulo Dashboard.
 * Uses TeaApp which handles all routing automatically when pages is provided.
 */
const StandaloneModuloDashboard: React.FC = () => <TeaApp name={APP_NAME} subtitle={SUBTITLE} pages={PAGES} />;

// Render the standalone app to DOM
const rootElement = document.getElementById('root');
if (rootElement) {
    createRoot(rootElement).render(
        <StrictMode>
            <StandaloneModuloDashboard />
        </StrictMode>,
    );
}

export default StandaloneModuloDashboard;

// Re-export the embeddable page component for use in other apps
export { default as ModuloDashboard } from './components/ModuloDashboard';
