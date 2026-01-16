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
import { TTApp, TTNav, TTPage } from '@teatype/components';

const StudentDB = () => {
    return (
        <TTApp name='HSDB Dashboard'>
            <TTNav subtitle='Select a module to get started' />

            <TTPage
                id='models'
                title='Model Selection'
                description='Select and configure AI models for your student database application.'
                icon={<ModelIcon />}
            >
                <p>Model selection content goes here...</p>
            </TTPage>

            <TTPage
                id='database'
                title='Database Management'
                description='View and manage student records in the database.'
                icon={<DatabaseIcon />}
            >
                <p>Database management content goes here...</p>
            </TTPage>

            <TTPage
                id='settings'
                title='Settings'
                description='Configure application preferences and system settings.'
                icon={<SettingsIcon />}
            >
                <p>Settings content goes here...</p>
            </TTPage>
        </TTApp>
    );
};

export default StudentDB;
