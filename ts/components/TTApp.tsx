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

import { createContext, useCallback, useContext, useState } from 'react';

// Style
import './style/TTApp.scss';

export interface iPageInfo {
    id: string;
    title: string;
    description?: string;
    icon?: React.ReactNode;
}

interface iTTAppContext {
    appName: string;
    activePage: string | null;
    pages: iPageInfo[];
    registerPage: (page: iPageInfo) => void;
    navigateTo: (pageId: string | null) => void;
}

const TTAppContext = createContext<iTTAppContext | null>(null);

export const useTTApp = () => {
    const context = useContext(TTAppContext);
    if (!context) {
        throw new Error('useTTApp must be used within a TTApp');
    }
    return context;
};

interface iTTAppProps {
    children: React.ReactNode;
    defaultPage?: string;
    name: string;
}

const TTApp: React.FC<iTTAppProps> = ({ children, defaultPage = null, name }) => {
    const [activePage, setActivePage] = useState<string | null>(defaultPage);
    const [pages, setPages] = useState<iPageInfo[]>([]);

    const registerPage = useCallback((page: iPageInfo) => {
        setPages((prev) => {
            if (prev.some((p) => p.id === page.id)) return prev;
            return [...prev, page];
        });
    }, []);

    const navigateTo = useCallback((pageId: string | null) => {
        setActivePage(pageId);
    }, []);

    return (
        <TTAppContext.Provider value={{ appName: name, activePage, pages, registerPage, navigateTo }}>
            <div id='tt-app'>{children}</div>
        </TTAppContext.Provider>
    );
};

export default TTApp;

export { TTApp };
