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
import { Routes, Route } from 'react-router-dom';

// Components
import ModuloStatusModal from './components/ModuloStatusModal';
import { iPageInfo, TeaApp, TeaNav, TeaPage } from '../../../components';

// Icons
import { SettingsIcon } from '../../../icons';

const APP_NAME = 'Modulo Dashboard';
const PAGES: iPageInfo[] = [
    {
        title: 'Dashboard',
        path: '/dashboard',
        content: ModuloStatusModal,
        longDescription: 'Monitor and control your Modulo application with live status, logs, and command execution.',
        shortDescription: 'Operations Pulse Dashboard',
        icon: <SettingsIcon />,
        tags: ['Admin', 'Modulo'],
    },
];

const ModuloDashboard = () => {
    return (
        <TeaApp name={APP_NAME}>
            <Routes>
                {/* Home page - Navigation */}
                <Route
                    path='/'
                    element={
                        <TeaNav
                            appName={APP_NAME}
                            filtersEnabled={false}
                            pages={PAGES}
                            subtitle='Lightweight dashboard for monitoring and controlling Modulo'
                        />
                    }
                />

                {/* Dashboard and other pages */}
                {PAGES.map((page) => {
                    const PageContent = page.content;
                    return (
                        <Route
                            key={page.path}
                            path={page.path}
                            element={
                                <TeaPage
                                    appName={APP_NAME}
                                    title={page.title}
                                    description={page.longDescription}
                                    tags={page.tags}
                                >
                                    {PageContent && <PageContent />}
                                </TeaPage>
                            }
                        />
                    );
                })}
            </Routes>
        </TeaApp>
    );
};

export default ModuloDashboard;
