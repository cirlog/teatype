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

// Icons
import { FlagEN, FlagDE, FlagTR } from '@teatype/icons';

// Utility
import { Store } from '@teatype/toolkit/Store';

export type tLanguage = 'en' | 'de' | 'tr';
export type tTheme = 'dark' | 'flow' | 'light';

// Storage key prefix for all TeaType settings
export const TEATYPE_STORAGE_PREFIX = 'teatype';
export const TEATYPE_SETTINGS_INITIALIZED_KEY = 'teatype.settings._initialized';

// Default settings values
export const DEFAULT_SETTINGS = {
    theme: 'flow' as tTheme,
    pageWidth: 100,
    language: 'en' as tLanguage,
};

/**
 * Utility function to clear all TeaType settings from storage.
 * Can be used outside of React context (e.g., in utility scripts).
 */
export const clearAllTeaTypeSettings = (): void => {
    Store.local.clearByPrefix(TEATYPE_STORAGE_PREFIX);
    Store.session.clearByPrefix(TEATYPE_STORAGE_PREFIX);
    Store.memory.clearByPrefix(TEATYPE_STORAGE_PREFIX);
};

export interface LanguageInfo {
    code: tLanguage;
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
    theme: tTheme;
    pageWidth: number;
    language: tLanguage;

    setIsSettingsOpen: (open: boolean) => void;
    setTheme: (theme: tTheme) => void;
    setPageWidth: (width: number) => void;
    setLanguage: (lang: tLanguage) => void;
    /** Clears all TeaType settings and resets to defaults */
    clearSettings: () => void;
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
    onLanguageChange?: (lang: tLanguage) => void;
    /** Default language if not set in localStorage */
    defaultLanguage?: tLanguage;
}

export const TeaSettingsProvider: React.FC<TeaSettingsProviderProps> = ({
    children,
    onLanguageChange,
    defaultLanguage = 'en',
}) => {
    // Initialize defaults on first run
    const initializeDefaults = useCallback(() => {
        if (typeof window === 'undefined') return;

        const isInitialized = Store.local.get(TEATYPE_SETTINGS_INITIALIZED_KEY);
        if (!isInitialized) {
            // First time app initialization - set defaults
            Store.local.set('teatype.settings.theme', DEFAULT_SETTINGS.theme);
            Store.local.set('teatype.settings.pageWidth', String(DEFAULT_SETTINGS.pageWidth));
            Store.local.set('teatype.settings.language', defaultLanguage || DEFAULT_SETTINGS.language);
            Store.local.set(TEATYPE_SETTINGS_INITIALIZED_KEY, 'true');
        }
    }, [defaultLanguage]);

    // Run initialization on mount
    useEffect(() => {
        initializeDefaults();
    }, [initializeDefaults]);

    const [theme, setThemeState] = useState<tTheme>(() => {
        if (typeof window !== 'undefined') {
            return (Store.local.get('teatype.settings.theme') as tTheme) || DEFAULT_SETTINGS.theme;
        }
        return DEFAULT_SETTINGS.theme;
    });

    const [pageWidth, setPageWidthState] = useState<number>(() => {
        if (typeof window !== 'undefined') {
            const saved = Store.local.get('teatype.settings.pageWidth') as string | null;
            return saved ? parseInt(saved, 10) : DEFAULT_SETTINGS.pageWidth;
        }
        return DEFAULT_SETTINGS.pageWidth;
    });

    const [language, setLanguageState] = useState<tLanguage>(() => {
        if (typeof window !== 'undefined') {
            return (Store.local.get('teatype.settings.language') as tLanguage) || defaultLanguage;
        }
        return defaultLanguage;
    });

    const [isSettingsOpen, setIsSettingsOpen] = useState(false);

    const setTheme = (newTheme: tTheme) => {
        setThemeState(newTheme);
        Store.local.set('teatype.settings.theme', newTheme);
    };

    const setPageWidth = (width: number) => {
        setPageWidthState(width);
        Store.local.set('teatype.settings.pageWidth', String(width));
    };

    const setLanguage = useCallback(
        (lang: tLanguage) => {
            setLanguageState(lang);
            Store.local.set('teatype.settings.language', lang);
            document.documentElement.setAttribute('lang', lang);
            onLanguageChange?.(lang);
        },
        [onLanguageChange],
    );

    /**
     * Clears all TeaType-specific settings from all storage types and resets to defaults.
     */
    const clearSettings = useCallback(() => {
        // Clear all teatype-prefixed keys from all storage types
        Store.local.clearByPrefix(TEATYPE_STORAGE_PREFIX);
        Store.session.clearByPrefix(TEATYPE_STORAGE_PREFIX);
        Store.memory.clearByPrefix(TEATYPE_STORAGE_PREFIX);

        // Reset state to defaults
        setThemeState(DEFAULT_SETTINGS.theme);
        setPageWidthState(DEFAULT_SETTINGS.pageWidth);
        setLanguageState(defaultLanguage || DEFAULT_SETTINGS.language);

        // Re-apply defaults to storage (mark as initialized again)
        Store.local.set('teatype.settings.theme', DEFAULT_SETTINGS.theme);
        Store.local.set('teatype.settings.pageWidth', String(DEFAULT_SETTINGS.pageWidth));
        Store.local.set('teatype.settings.language', defaultLanguage || DEFAULT_SETTINGS.language);
        Store.local.set(TEATYPE_SETTINGS_INITIALIZED_KEY, 'true');

        // Apply to DOM
        document.documentElement.setAttribute('data-theme', DEFAULT_SETTINGS.theme);
        document.documentElement.style.setProperty('--tea-pageWidth', `${DEFAULT_SETTINGS.pageWidth}%`);
        document.documentElement.setAttribute('lang', defaultLanguage || DEFAULT_SETTINGS.language);

        onLanguageChange?.(defaultLanguage || DEFAULT_SETTINGS.language);
    }, [defaultLanguage, onLanguageChange]);

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
    }, [theme]);

    useEffect(() => {
        document.documentElement.style.setProperty('--tea-pageWidth', `${pageWidth}%`);
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
                clearSettings,
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
    const { theme, setTheme, pageWidth, setPageWidth, language, setLanguage, clearSettings } = useTeaSettings();
    const [showClearConfirm, setShowClearConfirm] = useState(false);

    const handleClearSettings = () => {
        clearSettings();
        setShowClearConfirm(false);
    };

    const themes: { id: tTheme; label: string; description: string }[] = [
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

                {(Store.memory.get('devMode') as boolean) && (
                    <section className='tea-settings-section tea-settings-section--danger'>
                        <h3>Reset Settings</h3>

                        {showClearConfirm ? (
                            <div className='tea-settings-confirm'>
                                <span>Are you sure?</span>
                                <button
                                    className='tea-settings-confirm-btn tea-settings-confirm-btn--cancel'
                                    onClick={() => setShowClearConfirm(false)}
                                >
                                    Cancel
                                </button>
                                <button
                                    className='tea-settings-confirm-btn tea-settings-confirm-btn--confirm'
                                    onClick={handleClearSettings}
                                >
                                    Yes, Reset
                                </button>
                            </div>
                        ) : (
                            <button className='tea-settings-clear-btn' onClick={() => setShowClearConfirm(true)}>
                                Clear All Settings
                            </button>
                        )}
                    </section>
                )}
            </div>
        </div>
    );
};
