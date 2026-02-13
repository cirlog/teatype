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

import en from './en.json';
import de from './de.json';
import tr from './tr.json';

import type { Translations } from '../../../../hooks';

/**
 * Flattens a nested object into dot-notation keys.
 * { dashboard: { title: 'Dashboard' } } -> { 'dashboard.title': 'Dashboard' }
 */
const flatten = (obj: Record<string, unknown>, prefix = ''): Record<string, string> => {
    return Object.entries(obj).reduce(
        (acc, [key, value]) => {
            const path = prefix ? `${prefix}.${key}` : key;
            if (value && typeof value === 'object' && !Array.isArray(value)) {
                Object.assign(acc, flatten(value as Record<string, unknown>, path));
            } else {
                acc[path] = String(value);
            }
            return acc;
        },
        {} as Record<string, string>,
    );
};

/**
 * Translation dictionaries for ModuloDashboard.
 * Use with the `useTranslation` hook from @teatype/hooks.
 *
 * @example
 * import { useTranslation } from '@teatype/hooks';
 * import { translations } from './i18n';
 *
 * const MyComponent = () => {
 *     const { t } = useTranslation(translations);
 *     return <h1>{t('dashboard.title')}</h1>;
 * };
 */
export const translations: Translations = {
    en: flatten(en),
    de: flatten(de),
    tr: flatten(tr),
};

export default translations;
