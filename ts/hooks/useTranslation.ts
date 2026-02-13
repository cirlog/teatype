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

import { useCallback, useMemo } from 'react';
import { useTeaSettings, Language } from '../components/TeaApp/TeaSettings';

/**
 * Translation dictionary type.
 * Keys are dot-separated paths, values are the translated strings.
 */
export type TranslationDict = Record<string, string>;

/**
 * Translations object containing all language dictionaries.
 */
export type Translations = Partial<Record<Language, TranslationDict>>;

/**
 * Simple translation hook that integrates with TeaSettings.
 *
 * @example
 * // Define translations
 * const translations = {
 *     en: {
 *         'welcome': 'Welcome',
 *         'dashboard.title': 'Dashboard',
 *         'dashboard.description': 'Monitor your application',
 *     },
 *     de: {
 *         'welcome': 'Willkommen',
 *         'dashboard.title': 'Dashboard',
 *         'dashboard.description': 'Überwachen Sie Ihre Anwendung',
 *     },
 * };
 *
 * // Use in component
 * const { t, language } = useTranslation(translations);
 * return <h1>{t('dashboard.title')}</h1>;
 *
 * @param translations - Object with language codes as keys and translation dictionaries as values
 * @param fallbackLanguage - Language to use if current language is not available (default: 'en')
 */
export const useTranslation = (translations: Translations, fallbackLanguage: Language = 'en') => {
    const { language } = useTeaSettings();

    const dict = useMemo(() => {
        return translations[language] || translations[fallbackLanguage] || {};
    }, [translations, language, fallbackLanguage]);

    /**
     * Translate a key to the current language.
     * Returns the key itself if no translation is found.
     *
     * @param key - The translation key (supports dot notation like 'section.subsection.key')
     * @param params - Optional parameters for interpolation (e.g., { name: 'John' } for 'Hello {{name}}')
     */
    const t = useCallback(
        (key: string, params?: Record<string, string | number>): string => {
            let value = dict[key];

            // If not found, return the key
            if (value === undefined) {
                console.warn(`Translation missing for key: "${key}" in language: "${language}"`);
                return key;
            }

            // Simple interpolation: replace {{param}} with value
            if (params) {
                Object.entries(params).forEach(([param, val]) => {
                    value = value.replace(new RegExp(`\\{\\{${param}\\}\\}`, 'g'), String(val));
                });
            }

            return value;
        },
        [dict, language],
    );

    return {
        t,
        language,
    };
};

export default useTranslation;
