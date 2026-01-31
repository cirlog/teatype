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
import { useState, useMemo } from 'react';
import { NavLink } from 'react-router-dom';

// Components
import { iPageInfo } from './TeaApp';

// Style
import './style/TeaNav.scss';

interface iTeaNavProps {
    appName: string;
    filtersEnabled?: boolean;
    navType?: 'apps';
    pages: iPageInfo[];
    subtitle?: string;
}

interface iAppNavProps {
    appName: string;
    filtersEnabled?: boolean;
    pages: iPageInfo[];
    subtitle?: string;
}

const AppNav: React.FC<iAppNavProps> = (props) => {
    const [selectedTags, setSelectedTags] = useState<string[]>([]);

    // Collect all unique tags from pages
    const allTags = useMemo(() => {
        const tags = new Set<string>();
        props.pages.forEach((page) => {
            page.tags?.forEach((tag) => tags.add(tag));
        });
        return Array.from(tags).sort();
    }, [props.pages]);

    // Filter pages based on selected tags
    const filteredPages = useMemo(() => {
        if (selectedTags.length === 0) return props.pages;
        return props.pages.filter((page) => page.tags?.some((tag) => selectedTags.includes(tag)));
    }, [props.pages, selectedTags]);

    const filtersEnabled = useMemo(() => props.filtersEnabled ?? true, [props.filtersEnabled]);

    const toggleTag = (tag: string) => {
        setSelectedTags((prev) => (prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]));
    };

    const clearFilters = () => {
        setSelectedTags([]);
    };

    return (
        <>
            <header className='tea-nav-header'>
                <h1 className='tea-nav-title'>{props.appName}</h1>
                {props.subtitle && <p className='tea-nav-subtitle'>{props.subtitle}</p>}
            </header>

            {filtersEnabled && allTags.length > 0 && (
                <div className='tea-nav-filter'>
                    <div className='tea-nav-filter-tags'>
                        {allTags.map((tag) => (
                            <button
                                key={tag}
                                className={`tea-nav-filter-tag ${selectedTags.includes(tag) ? 'active' : ''}`}
                                onClick={() => toggleTag(tag)}
                            >
                                {tag}
                            </button>
                        ))}
                    </div>
                    {selectedTags.length > 0 && (
                        <button className='tea-nav-filter-clear' onClick={clearFilters}>
                            Clear filters
                        </button>
                    )}
                </div>
            )}

            <main className='tea-nav-grid'>
                {filteredPages.map((page, index) => (
                    <NavLink
                        key={page.path}
                        to={page.path}
                        className='tea-nav-tile'
                        style={{ animationDelay: `${index * 0.05}s` }}
                    >
                        <div className='tea-nav-tile-icon'>{page.icon || page.title.charAt(0).toUpperCase()}</div>

                        <div className='tea-nav-tile-content'>
                            <h2 className='tea-nav-tile-title'>{page.title}</h2>

                            {page.shortDescription && (
                                <p className='tea-nav-tile-description'>{page.shortDescription}</p>
                            )}
                        </div>

                        <svg
                            className='tea-nav-tile-arrow'
                            width='20'
                            height='20'
                            viewBox='0 0 24 24'
                            fill='none'
                            stroke='currentColor'
                            strokeWidth='2'
                            strokeLinecap='round'
                            strokeLinejoin='round'
                        >
                            <path d='M5 12h14M12 5l7 7-7 7' />
                        </svg>
                    </NavLink>
                ))}

                {filteredPages.length === 0 && (
                    <div className='tea-nav-empty'>
                        <p>No apps match the selected filters</p>
                        <button onClick={clearFilters}>Clear filters</button>
                    </div>
                )}
            </main>
        </>
    );
};

// TODO: implement the exact lockkliye sidebar as additional nav type
// TODO: Also implement the taskbar as a teatype component
// TODO: Enforce Tea compnents usage in lockkliye as very first production app
const TeaNav: React.FC<iTeaNavProps> = (props) => {
    const navType = 'apps'; // Currently only 'apps' type is supported
    let navContent = null;
    if (navType === 'apps') {
        navContent = (
            <AppNav
                appName={props.appName}
                filtersEnabled={props.filtersEnabled}
                pages={props.pages}
                subtitle={props.subtitle}
            />
        );
    }
    return <nav id='tea-nav'>{navContent}</nav>;
};

export default TeaNav;

export { TeaNav };
