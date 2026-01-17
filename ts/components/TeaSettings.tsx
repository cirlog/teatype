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
import React, { createContext, useContext, useState, useEffect } from 'react';

export type Theme = 'dark' | 'flow' | 'light';

interface TeaSettingsContextValue {
    isSettingsOpen: boolean;
    theme: Theme;

    setIsSettingsOpen: (open: boolean) => void;
    setTheme: (theme: Theme) => void;
}

const TeaSettingsContext = createContext<TeaSettingsContextValue | null>(null);

export const useTeaSettings = () => {
    const context = useContext(TeaSettingsContext);
    if (!context) {
        throw new Error('useTeaSettings must be used within TeaSettingsProvider');
    }
    return context;
};

interface TeaSettingsProviderProps {
    children: React.ReactNode;
}

export const TeaSettingsProvider: React.FC<TeaSettingsProviderProps> = ({ children }) => {
    const [theme, setThemeState] = useState<Theme>(() => {
        if (typeof window !== 'undefined') {
            return (localStorage.getItem('tea-theme') as Theme) || 'flow';
        }
        return 'flow';
    });

    const [isSettingsOpen, setIsSettingsOpen] = useState(false);

    const setTheme = (newTheme: Theme) => {
        setThemeState(newTheme);
        localStorage.setItem('tea-theme', newTheme);
    };

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
    }, [theme]);

    return (
        <TeaSettingsContext.Provider
            value={{
                theme,
                setTheme,
                isSettingsOpen,
                setIsSettingsOpen,
            }}
        >
            {children}
        </TeaSettingsContext.Provider>
    );
};

interface TeaSettingsPanelProps {
    onClose: () => void;
}

export const TeaSettingsPanel: React.FC<TeaSettingsPanelProps> = ({ onClose }) => {
    const { theme, setTheme } = useTeaSettings();

    const themes: { id: Theme; label: string; description: string }[] = [
        { id: 'dark', label: 'Dark', description: 'Black gradient with orange accents' },
        { id: 'flow', label: 'Flow', description: 'Deep blue gradient with purple accents' },
        { id: 'light', label: 'Light', description: 'Clean white with subtle shadows' },
    ];

    return (
        <div className='tea-settings-panel'>
            <div className='tea-settings-header'>
                <h2>Settings</h2>
                <button className='tea-settings-close' onClick={onClose} aria-label='Close settings'>
                    <svg width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='currentColor' strokeWidth='2'>
                        <path d='M18 6L6 18M6 6l12 12' />
                    </svg>
                </button>
            </div>

            <div className='tea-settings-content'>
                <section className='tea-settings-section'>
                    <h3>Theme</h3>
                    <div className='tea-settings-theme-grid'>
                        {themes.map((t) => (
                            <button
                                key={t.id}
                                className={`tea-settings-theme-option ${theme === t.id ? 'active' : ''}`}
                                onClick={() => setTheme(t.id)}
                            >
                                <div className={`tea-settings-theme-preview theme-${t.id}`} />
                                <span className='tea-settings-theme-label'>{t.label}</span>
                                <span className='tea-settings-theme-desc'>{t.description}</span>
                            </button>
                        ))}
                    </div>
                </section>
            </div>
        </div>
    );
};
