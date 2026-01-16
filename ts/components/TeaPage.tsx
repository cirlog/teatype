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
import { TeaInfotip } from './TeaInfotip';
import { TeaTags } from './TeaTags';

// Icons
import { ArrowIcon } from '../icons';

// Style
import './style/TeaPage.scss';

interface iTeaPageProps {
    appName?: string;
    backPath?: string;
    children?: React.ReactNode;
    description?: string;
    tags?: string[];
    title: string;
}

const TeaPage: React.FC<iTeaPageProps> = ({ appName, backPath = '/', children, description, tags, title }) => {
    const navigate = useNavigate();

    return (
        <div className='tea-page'>
            <header className='tea-page-header'>
                <button className='tea-page-back' onClick={() => navigate(backPath)} aria-label='Go back'>
                    <ArrowIcon />
                </button>

                <div className='tea-page-header-content'>
                    {appName && <p className='tea-page-flare'>{appName}</p>}
                    <div className='tea-page-title-row'>
                        <h1 className='tea-page-title'>{title}</h1>
                        {description && <TeaInfotip position='right'>{description}</TeaInfotip>}
                    </div>
                    {tags && <TeaTags className='tea-page-tags' tags={tags} />}
                </div>
            </header>

            <main className='tea-page-main'>{children}</main>
        </div>
    );
};

export default TeaPage;

export { TeaPage };
