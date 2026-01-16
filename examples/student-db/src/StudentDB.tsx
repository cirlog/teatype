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

import { Routes, Route } from 'react-router-dom';

// Components
import { iPageInfo, TTApp, TTNav, TTPage } from '@teatype/components';

import { DatabaseIcon, ModelsIcon, SettingsIcon } from '@teatype/icons';

const APP_NAME = 'Student DB Dashboard';
const PAGES: iPageInfo[] = [
    {
        title: 'Model Selection',
        path: '/models',
        description: 'Select and configure AI models for your student database application.',
        icon: <ModelsIcon />,
    },
    {
        title: 'Database Management',
        path: '/database',
        description: 'View and manage student records in the database.',
        icon: <DatabaseIcon />,
    },
    {
        title: 'Settings',
        path: '/settings',
        description: 'Configure application preferences and system settings.',
        icon: <SettingsIcon />,
    },
];

const StudentDB = () => {
    return (
        <TTApp name={APP_NAME}>
            <Routes>
                <Route
                    path='/'
                    element={
                        <TTNav appName={APP_NAME} pages={PAGES} subtitle='Test-Application for the HSDB Server OEM' />
                    }
                />
                {PAGES.map((page) => (
                    <Route
                        key={page.path}
                        path={page.path}
                        element={
                            <TTPage appName={APP_NAME} title={page.title} description={page.description}>
                                <p>{page.title} content goes here...</p>
                            </TTPage>
                        }
                    />
                ))}
            </Routes>
        </TTApp>
    );
};

export default StudentDB;
