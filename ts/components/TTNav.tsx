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

// Components
import { useTTApp } from './TTApp';

// Style
import './style/TTNav.scss';

interface iTTNavProps {
    subtitle?: string;
}

const TTNav: React.FC<iTTNavProps> = ({ subtitle }) => {
    const { appName, activePage, pages, navigateTo } = useTTApp();

    // Don't show nav when a page is active
    if (activePage !== null) return null;

    return (
        <div className='tt-nav'>
            <header className='tt-nav-header'>
                <h1 className='tt-nav-title'>{appName}</h1>
                {subtitle && <p className='tt-nav-subtitle'>{subtitle}</p>}
            </header>

            <div className='tt-nav-grid'>
                {pages.map((page, index) => (
                    <button
                        key={page.id}
                        className='tt-nav-tile'
                        onClick={() => navigateTo(page.id)}
                        style={{ animationDelay: `${index * 0.05}s` }}
                    >
                        {page.icon && <div className='tt-nav-tile-icon'>{page.icon}</div>}
                        <div className='tt-nav-tile-content'>
                            <h2 className='tt-nav-tile-title'>{page.title}</h2>
                            {page.description && <p className='tt-nav-tile-description'>{page.description}</p>}
                        </div>
                        <svg
                            className='tt-nav-tile-arrow'
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
                    </button>
                ))}
            </div>
        </div>
    );
};

export default TTNav;

export { TTNav };
