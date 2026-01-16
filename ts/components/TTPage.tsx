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

import { useNavigate } from 'react-router-dom';

// Components
import { TTInfotip } from './TTInfotip';

// Icons
import { ArrowIcon } from '../icons';

// Style
import './style/TTPage.scss';

interface iTTPageProps {
    appName?: string;
    backPath?: string;
    children?: React.ReactNode;
    description?: string;
    title: string;
}

const TTPage: React.FC<iTTPageProps> = ({ appName, backPath = '/', children, description, title }) => {
    const navigate = useNavigate();

    return (
        <div className='tt-page'>
            <header className='tt-page-header'>
                <button className='tt-page-back' onClick={() => navigate(backPath)} aria-label='Go back'>
                    <ArrowIcon />
                </button>

                <div className='tt-page-header-content'>
                    {appName && <p className='tt-page-flare'>{appName}</p>}
                    <div className='tt-page-title-row'>
                        <h1 className='tt-page-title'>{title}</h1>
                        {description && <TTInfotip position='right'>{description}</TTInfotip>}
                    </div>
                </div>
            </header>

            <main className='tt-page-main'>{children}</main>
        </div>
    );
};

export default TTPage;

export { TTPage };
