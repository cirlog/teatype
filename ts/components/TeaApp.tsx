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
import { BrowserRouter } from 'react-router-dom';

// Components
import { TeaSettingsProvider, TeaSettingsPanel, useTeaSettings } from './TeaSettings';

// Icons
import { SettingsIcon } from '../icons';

// Style
import './style/TeaApp.scss';
import './style/TeaSettings.scss';

interface iPageInfo {
    content?: React.FC;
    icon?: React.ReactNode;
    longDescription?: string;
    path: string;
    shortDescription?: string;
    tags?: string[];
    title: string;
}

interface iTeaAppProps {
    children: React.ReactNode;
    name: string;
}

const TeaAppContent: React.FC<iTeaAppProps> = (props) => {
    const { isSettingsOpen, setIsSettingsOpen } = useTeaSettings();

    return (
        <div id='tea-app' data-app-name={props.name} className={isSettingsOpen ? 'settings-open' : ''}>
            <button
                className='tea-app-settings-toggle'
                onClick={() => setIsSettingsOpen(!isSettingsOpen)}
                aria-label='Toggle settings'
            >
                <SettingsIcon />
            </button>

            <div className='tea-app-content'>{props.children}</div>

            <aside className='tea-app-settings-sidebar'>
                <TeaSettingsPanel onClose={() => setIsSettingsOpen(false)} />
            </aside>
        </div>
    );
};

const TeaApp: React.FC<iTeaAppProps> = (props) => {
    return (
        <BrowserRouter>
            <TeaSettingsProvider>
                <TeaAppContent name={props.name}>{props.children}</TeaAppContent>
            </TeaSettingsProvider>
        </BrowserRouter>
    );
};

export default TeaApp;

export { TeaApp };

export type { iPageInfo };
