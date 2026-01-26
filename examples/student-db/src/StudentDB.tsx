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
import { HSDBAdmin } from '@teatype/apps';
import { QueryBuilder } from '@teatype/apps';
import { iPageInfo, TeaApp, TeaNav, TeaPage } from '@teatype/components';

import { DatabaseIcon, ModelsIcon, ArrowIcon } from '@teatype/icons';

// Local components
import SubNavDemo from './SubNavDemo';

const APP_NAME = 'Student DB Dashboard';
const PAGES: iPageInfo[] = [
    {
        title: 'Database Management',
        path: '/database',
        content: HSDBAdmin,
        longDescription: 'View and manage student (and adjacent) records in the hybrid database.',
        shortDescription: 'Manage Student Records',
        icon: <DatabaseIcon />,
        tags: ['Admin', 'HSDB'],
    },
    {
        title: 'Data Query Builder',
        path: '/data-query-builder',
        content: QueryBuilder,
        longDescription: 'Build and execute custom queries against the HSDB server to fetch student and related data.',
        shortDescription: 'Build Custom Data Queries',
        icon: <ModelsIcon />,
        tags: ['Admin', 'Config', 'HSDB', 'Test'],
    },
    {
        title: 'SubNav Demo',
        path: '/subnav-demo',
        content: SubNavDemo,
        longDescription: 'Demonstration of the TeaSubNav component with tab-style navigation and hover effects.',
        shortDescription: 'SubNav Component Demo',
        icon: null,
        tags: ['Dev', 'Test'],
    },
];

const StudentDB = () => {
    return (
        <TeaApp name={APP_NAME}>
            <Routes>
                <Route
                    path='/'
                    element={
                        <TeaNav
                            appName={APP_NAME}
                            filtersEnabled={false}
                            pages={PAGES}
                            subtitle='Test-Application for the HSDB Server OEM'
                        />
                    }
                />
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

export default StudentDB;
