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
import React, { useMemo, useState } from 'react';

// Components
import { TeaButton } from './TeaInput/TeaButton';
import { TeaSelect } from './TeaInput/TeaInput';
import { TeaSlider } from './TeaInput/TeaSlider';

// Style
import './style/TeaSettingsPage.scss';

// What a setting is edited with
export type tTeaSettingControl =
    | { type: 'toggle'; value: boolean; onChange: (value: boolean) => void }
    | {
          type: 'slider';
          value: number;
          min: number;
          max: number;
          step?: number;
          unit?: string;
          onChange: (value: number) => void;
      }
    | { type: 'select'; value: string; options: { value: string; label: string }[]; onChange: (value: string) => void }
    | { type: 'button'; label: string; onClick: () => void; icon?: React.ReactNode; theme?: 'default' | 'danger' }
    | { type: 'buttons'; buttons: { id: string; label: string; onClick: () => void; theme?: 'default' | 'danger' }[] }
    | { type: 'custom'; render: () => React.ReactNode };

export interface iTeaSettingsItem {
    id: string;
    label: string;
    description?: string;
    /** Marks this one setting as meant for developers, also if the group is not */
    developer?: boolean;
    control: tTeaSettingControl;
}

export interface iTeaSettingsGroup {
    id: string;
    title?: string;
    description?: string;
    /** Marks every setting of the group as meant for developers */
    developer?: boolean;
    items: iTeaSettingsItem[];
}

export interface iTeaSettingsCategory {
    id: string;
    label: string;
    icon?: React.ReactNode;
    description?: string;
    /** Marks the whole category as meant for developers: it gets a badge and sorts below the others */
    developer?: boolean;
    groups: iTeaSettingsGroup[];
}

export interface iTeaSettingsPageProps {
    categories: iTeaSettingsCategory[];
    title?: string;
    /** Shows a back button in the header */
    onClose?: () => void;
    /** Controlled category, the page keeps its own selection if left out */
    activeCategoryId?: string;
    onCategoryChange?: (categoryId: string) => void;
    /** Shows a search field that filters the settings of all categories (default: true) */
    searchable?: boolean;
    className?: string;
}

const DeveloperBadge: React.FC = () => (
    <span className='tea-settings-page__badge' title='Meant for developers'>
        Developer
    </span>
);

const Toggle: React.FC<{ value: boolean; label: string; onChange: (value: boolean) => void }> = ({
    value,
    label,
    onChange,
}) => (
    <button
        type='button'
        role='switch'
        aria-checked={value}
        aria-label={label}
        className={`tea-settings-page__toggle ${value ? 'tea-settings-page__toggle--on' : ''}`}
        onClick={() => onChange(!value)}
    >
        <span className='tea-settings-page__toggle-knob' />
    </button>
);

const renderControl = (item: iTeaSettingsItem): React.ReactNode => {
    const control = item.control;
    switch (control.type) {
        case 'toggle':
            return <Toggle value={control.value} label={item.label} onChange={control.onChange} />;
        case 'slider':
            return (
                <div className='tea-settings-page__slider'>
                    <TeaSlider
                        value={control.value}
                        min={control.min}
                        max={control.max}
                        step={control.step}
                        onChange={control.onChange}
                        formatValue={(value) => `${value}${control.unit ?? ''}`}
                    />
                </div>
            );
        case 'select':
            return (
                <TeaSelect
                    value={control.value}
                    options={control.options}
                    onChange={(event) => control.onChange(event.target.value)}
                />
            );
        case 'button':
            return (
                <TeaButton theme={control.theme} icon={control.icon} onClick={control.onClick}>
                    {control.label}
                </TeaButton>
            );
        case 'buttons':
            return (
                <div className='tea-settings-page__buttons'>
                    {control.buttons.map((button) => (
                        <TeaButton key={button.id} theme={button.theme} onClick={button.onClick}>
                            {button.label}
                        </TeaButton>
                    ))}
                </div>
            );
        case 'custom':
            return control.render();
    }
};

const matches = (query: string, ...texts: (string | undefined)[]): boolean =>
    texts.some((text) => text?.toLowerCase().includes(query));

/**
 * A page of settings, built from a description: categories on the left, the groups of settings of the chosen
 * category on the right. Settings for developers are marked as such, they can be a whole category, a group or a
 * single setting.
 */
export const TeaSettingsPage: React.FC<iTeaSettingsPageProps> = ({
    categories,
    title = 'Settings',
    onClose,
    activeCategoryId,
    onCategoryChange,
    searchable = true,
    className = '',
}) => {
    const [ownCategoryId, setOwnCategoryId] = useState<string | undefined>(undefined);
    const [query, setQuery] = useState('');

    // Developer categories come last
    const ordered = useMemo(
        () => [...categories].sort((a, b) => Number(!!a.developer) - Number(!!b.developer)),
        [categories],
    );

    const searching = query.trim().length > 0;
    const needle = query.trim().toLowerCase();
    const activeId = activeCategoryId ?? ownCategoryId ?? ordered[0]?.id;
    const chooseCategory = (id: string) => {
        setOwnCategoryId(id);
        onCategoryChange?.(id);
    };

    // While searching, every category contributes its matching settings
    const visible = useMemo(() => {
        const shown = searching ? ordered : ordered.filter((category) => category.id === activeId);
        return shown
            .map((category) => ({
                category,
                groups: category.groups
                    .map((group) => ({
                        ...group,
                        items: searching
                            ? group.items.filter((item) =>
                                  matches(needle, item.label, item.description, group.title, category.label),
                              )
                            : group.items,
                    }))
                    .filter((group) => group.items.length > 0),
            }))
            .filter((entry) => entry.groups.length > 0);
    }, [ordered, searching, needle, activeId]);

    return (
        <div className={`tea-settings-page ${className}`}>
            <header className='tea-settings-page__header'>
                {onClose && (
                    <button className='tea-settings-page__back' onClick={onClose} title='Back'>
                        ←
                    </button>
                )}
                <h1 className='tea-settings-page__title'>{title}</h1>
                {searchable && (
                    <input
                        className='tea-settings-page__search'
                        type='search'
                        placeholder='Search settings...'
                        value={query}
                        onChange={(event) => setQuery(event.target.value)}
                    />
                )}
            </header>

            <div className='tea-settings-page__body'>
                <nav className='tea-settings-page__nav'>
                    {ordered.map((category) => (
                        <button
                            key={category.id}
                            className={`tea-settings-page__nav-item ${
                                !searching && category.id === activeId ? 'tea-settings-page__nav-item--active' : ''
                            }`}
                            onClick={() => {
                                setQuery('');
                                chooseCategory(category.id);
                            }}
                        >
                            {category.icon && <span className='tea-settings-page__nav-icon'>{category.icon}</span>}
                            <span>{category.label}</span>
                            {category.developer && <DeveloperBadge />}
                        </button>
                    ))}
                </nav>

                <main className='tea-settings-page__content'>
                    {visible.length === 0 && <p className='tea-settings-page__empty'>No settings found.</p>}
                    {visible.map(({ category, groups }) => (
                        <section key={category.id} className='tea-settings-page__category'>
                            <h2 className='tea-settings-page__category-title'>
                                {category.label}
                                {category.developer && <DeveloperBadge />}
                            </h2>
                            {category.description && !searching && (
                                <p className='tea-settings-page__category-description'>{category.description}</p>
                            )}
                            {groups.map((group) => (
                                <div key={group.id} className='tea-settings-page__group'>
                                    {group.title && (
                                        <h3 className='tea-settings-page__group-title'>
                                            {group.title}
                                            {group.developer && !category.developer && <DeveloperBadge />}
                                        </h3>
                                    )}
                                    {group.description && (
                                        <p className='tea-settings-page__group-description'>{group.description}</p>
                                    )}
                                    <div className='tea-settings-page__items'>
                                        {group.items.map((item) => (
                                            <div key={item.id} className='tea-settings-page__item'>
                                                <div className='tea-settings-page__item-text'>
                                                    <span className='tea-settings-page__item-label'>
                                                        {item.label}
                                                        {item.developer && !group.developer && !category.developer && (
                                                            <DeveloperBadge />
                                                        )}
                                                    </span>
                                                    {item.description && (
                                                        <span className='tea-settings-page__item-description'>
                                                            {item.description}
                                                        </span>
                                                    )}
                                                </div>
                                                <div className='tea-settings-page__item-control'>
                                                    {renderControl(item)}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </section>
                    ))}
                </main>
            </div>
        </div>
    );
};

export default TeaSettingsPage;
