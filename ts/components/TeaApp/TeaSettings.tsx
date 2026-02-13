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
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

// Flag icons
import { FlagEN, FlagDE, FlagTR } from '@teatype/icons';

export type Theme = 'dark' | 'flow' | 'light';
export type Language = 'en' | 'de' | 'tr';

export interface LanguageInfo {
    code: Language;
    name: string;
    nativeName: string;
    Flag: React.FC; // SVG flag component
}

export const SUPPORTED_LANGUAGES: LanguageInfo[] = [
    { code: 'en', name: 'English', nativeName: 'English', Flag: FlagEN },
    { code: 'de', name: 'German', nativeName: 'Deutsch', Flag: FlagDE },
    { code: 'tr', name: 'Turkish', nativeName: 'Türkçe', Flag: FlagTR },
];

interface TeaSettingsContextValue {
    isSettingsOpen: boolean;
    theme: Theme;
    pageWidth: number;
    language: Language;

    setIsSettingsOpen: (open: boolean) => void;
    setTheme: (theme: Theme) => void;
    setPageWidth: (width: number) => void;
    setLanguage: (lang: Language) => void;
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
    /** Callback when language changes - use this to update your i18n instance */
    onLanguageChange?: (lang: Language) => void;
    /** Default language if not set in localStorage */
    defaultLanguage?: Language;
}

export const TeaSettingsProvider: React.FC<TeaSettingsProviderProps> = ({
    children,
    onLanguageChange,
    defaultLanguage = 'en',
}) => {
    const [theme, setThemeState] = useState<Theme>(() => {
        if (typeof window !== 'undefined') {
            return (localStorage.getItem('tea-theme') as Theme) || 'flow';
        }
        return 'flow';
    });

    const [pageWidth, setPageWidthState] = useState<number>(() => {
        if (typeof window !== 'undefined') {
            const saved = localStorage.getItem('tea-page-width');
            return saved ? parseInt(saved, 10) : 100;
        }
        return 100;
    });

    const [language, setLanguageState] = useState<Language>(() => {
        if (typeof window !== 'undefined') {
            return (localStorage.getItem('tea-language') as Language) || defaultLanguage;
        }
        return defaultLanguage;
    });

    const [isSettingsOpen, setIsSettingsOpen] = useState(false);

    const setTheme = (newTheme: Theme) => {
        setThemeState(newTheme);
        localStorage.setItem('tea-theme', newTheme);
    };

    const setPageWidth = (width: number) => {
        setPageWidthState(width);
        localStorage.setItem('tea-page-width', String(width));
    };

    const setLanguage = useCallback(
        (lang: Language) => {
            setLanguageState(lang);
            localStorage.setItem('tea-language', lang);
            document.documentElement.setAttribute('lang', lang);
            onLanguageChange?.(lang);
        },
        [onLanguageChange],
    );

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
    }, [theme]);

    useEffect(() => {
        document.documentElement.style.setProperty('--tea-page-width', `${pageWidth}%`);
    }, [pageWidth]);

    useEffect(() => {
        document.documentElement.setAttribute('lang', language);
    }, [language]);

    return (
        <TeaSettingsContext.Provider
            value={{
                theme,
                setTheme,
                pageWidth,
                setPageWidth,
                language,
                setLanguage,
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
    const { theme, setTheme, pageWidth, setPageWidth, language, setLanguage } = useTeaSettings();

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

                <section className='tea-settings-section'>
                    <h3>Language</h3>
                    <div className='tea-settings-language-grid'>
                        {SUPPORTED_LANGUAGES.map((lang) => (
                            <button
                                key={lang.code}
                                className={`tea-settings-flag-btn ${language === lang.code ? 'active' : ''}`}
                                onClick={() => setLanguage(lang.code)}
                                title={lang.nativeName}
                                aria-label={lang.name}
                            >
                                <span className='tea-settings-flag'>
                                    <lang.Flag />
                                </span>
                            </button>
                        ))}
                    </div>
                </section>

                <section className='tea-settings-section'>
                    <h3>Page Width</h3>
                    <div className='tea-settings-slider'>
                        <input
                            type='range'
                            min='50'
                            max='100'
                            step='5'
                            value={pageWidth}
                            onChange={(e) => setPageWidth(Number(e.target.value))}
                        />
                        <span className='tea-settings-slider-value'>{pageWidth}%</span>
                    </div>
                    <p className='tea-settings-hint'>Adjust the maximum width of page content.</p>
                </section>
            </div>
        </div>
    );
};
