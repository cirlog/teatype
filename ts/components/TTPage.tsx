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

import { useEffect } from 'react';

// Components
import { useTTApp } from './TTApp';
import { TTInfotip } from './TTInfotip';

// Style
import './style/TTPage.scss';

interface iTTPageProps {
    children?: React.ReactNode;
    description?: string;
    icon?: React.ReactNode;
    id: string;
    title: string;
}

const TTPage: React.FC<iTTPageProps> = ({ children, description, icon, id, title }) => {
    const { appName, activePage, registerPage, navigateTo } = useTTApp();

    useEffect(() => {
        registerPage({ id, title, description, icon });
    }, [id, title, description, icon, registerPage]);

    if (activePage !== id) return null;

    return (
        <div className='tt-page'>
            <header className='tt-page-header'>
                <button className='tt-page-back' onClick={() => navigateTo(null)} aria-label='Go back'>
                    <svg
                        width='24'
                        height='24'
                        viewBox='0 0 24 24'
                        fill='none'
                        stroke='currentColor'
                        strokeWidth='2'
                        strokeLinecap='round'
                        strokeLinejoin='round'
                    >
                        <path d='M19 12H5M12 19l-7-7 7-7' />
                    </svg>
                </button>
                <div className='tt-page-header-content'>
                    <p className='tt-page-flare'>{appName}</p>
                    <div className='tt-page-title-row'>
                        <h1 className='tt-page-title'>{title}</h1>
                        {description && (
                            <TTInfotip content={description} position='right'>
                                <span className='tt-page-info-icon'>i</span>
                            </TTInfotip>
                        )}
                    </div>
                </div>
            </header>
            <main className='tt-page-content'>{children}</main>
        </div>
    );
};

export default TTPage;

export { TTPage };
