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
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Components
import NotFound from '../Errors/NotFound';
import { TeaSettingsProvider, TeaSettingsPanel, useTeaSettings } from './TeaSettings';
import { TeaNav } from './TeaNav';
import { TeaPage } from './TeaPage';

// Icons
import { SettingsIcon } from '../../icons';

// Global styles (makes TeaApp self-contained)
import '../../style/globstyle.scss';

// Component styles
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
    /** Name of the application, displayed in header */
    name: string;
    /** Subtitle/description shown on the nav page */
    subtitle?: string;
    /**
     * Array of page definitions. When provided, routing is handled automatically.
     * If omitted, use `children` for custom routing.
     */
    pages?: iPageInfo[];
    /** Custom children content (used when pages is not provided) */
    children?: React.ReactNode;
    /**
     * Force showing the navigation home page even for single-page apps.
     * Default: false (single-page apps auto-redirect to the page)
     */
    forceShowNav?: boolean;
    /** Enable tag/filter functionality on nav page. Default: false */
    filtersEnabled?: boolean;
}

interface iTeaAppContentProps {
    name: string;
    children: React.ReactNode;
}

const TeaAppContent: React.FC<iTeaAppContentProps> = (props) => {
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

/**
 * TeaApp - Main application wrapper with settings panel and optional routing.
 *
 * For single-page apps (pages.length === 1), automatically redirects to that page
 * unless forceShowNav is set to true.
 */
const TeaApp: React.FC<iTeaAppProps> = ({
    name,
    subtitle,
    pages,
    children,
    forceShowNav = false,
    filtersEnabled = false,
}) => {
    const isSinglePage = pages && pages.length === 1 && !forceShowNav;
    const singlePage = isSinglePage ? pages[0] : null;

    // Determine content: automatic routing with pages, or custom children
    const content = pages ? (
        <Routes>
            {/* Home page - Navigation or redirect for single-page apps */}
            <Route
                path='/'
                element={
                    isSinglePage && singlePage ? (
                        <Navigate to={singlePage.path} replace />
                    ) : (
                        <TeaNav appName={name} filtersEnabled={filtersEnabled} pages={pages} subtitle={subtitle} />
                    )
                }
            />

            {/* All pages */}
            {pages.map((page) => {
                const PageContent = page.content;
                return (
                    <Route
                        key={page.path}
                        path={page.path}
                        element={
                            <TeaPage
                                appName={name}
                                title={page.title}
                                description={page.longDescription}
                                tags={page.tags}
                                hideBackButton={isSinglePage}
                            >
                                {PageContent && <PageContent />}
                            </TeaPage>
                        }
                    />
                );
            })}

            {/* 404 - Page not found */}
            <Route path='*' element={<NotFound />} />
        </Routes>
    ) : (
        children
    );

    return (
        <BrowserRouter>
            <TeaSettingsProvider>
                <TeaAppContent name={name}>{content}</TeaAppContent>
            </TeaSettingsProvider>
        </BrowserRouter>
    );
};

export default TeaApp;

export { TeaApp };

export type { iPageInfo, iTeaAppProps };
