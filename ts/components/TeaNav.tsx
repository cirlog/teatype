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

import { NavLink } from 'react-router-dom';

// Components
import { iPageInfo } from './TeaApp';

// Style
import './style/TeaNav.scss';

interface iTeaNavProps {
    appName: string;
    navType?: 'apps';
    pages: iPageInfo[];
    subtitle?: string;
}

const AppNavigation = (props) => {
    return (
        <>
            <header className='tea-nav-header'>
                <h1 className='tea-nav-title'>{props.appName}</h1>
                {props.subtitle && <p className='tea-nav-subtitle'>{props.subtitle}</p>}
            </header>

            <main className='tea-nav-grid'>
                {props.pages.map((page, index) => (
                    <NavLink
                        key={page.path}
                        to={page.path}
                        className='tea-nav-tile'
                        style={{ animationDelay: `${index * 0.05}s` }}
                    >
                        {page.icon && <div className='tea-nav-tile-icon'>{page.icon}</div>}

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
            </main>
        </>
    );
};

const TeaNav: React.FC<iTeaNavProps> = (props) => {
    const navType = 'apps'; // Currently only 'apps' type is supported
    let navContent = null;
    if (navType === 'apps') {
        navContent = <AppNavigation appName={props.appName} pages={props.pages} subtitle={props.subtitle} />;
    }

    return <nav id='tea-nav'>{navContent}</nav>;
};

export default TeaNav;

export { TeaNav };
