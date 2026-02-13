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
import { useRef, useState, useEffect, memo } from 'react';
import { useNavigate } from 'react-router-dom';

// Components
import { TeaInfotip } from '../TeaInfotip';
import { TeaTags } from '../TeaTags/TeaTags';

// Icons
import { ArrowIcon } from '../../icons';

// Style
import './style/TeaPage.scss';

interface iTeaPageProps {
    appName?: string;
    backPath?: string;
    children?: React.ReactNode;
    description?: string;
    hideBackButton?: boolean;
    tags?: string[];
    title: string;
}

interface iTeaPageState {
    isInfoHovered: boolean;
    scrollProgress: number;
}

const TeaPage: React.FC<iTeaPageProps> = (props) => {
    // Hooks
    const navigate = useNavigate();

    // State
    const [isInfoHovered, setIsInfoHovered] = useState<iTeaPageState['isInfoHovered']>(false);
    const [scrollProgress, setScrollProgress] = useState<iTeaPageState['scrollProgress']>(0);

    // Refs
    const mainRef = useRef<HTMLElement>(null);

    // Constants
    const backPath = props.backPath ?? '/';
    const hideBackButton = props.hideBackButton ?? false;

    // Track scroll position to apply progressive fade effect
    useEffect(() => {
        const mainEl = mainRef.current;
        if (!mainEl) return;

        const handleScroll = () => {
            // Calculate scroll progress (0-1) over the first 100px of scroll
            const scrollTop = mainEl.scrollTop;
            const progress = Math.min(scrollTop / 100, 1);
            setScrollProgress(progress);

            // Apply scroll progress as CSS custom property for smooth mask transition
            mainEl.style.setProperty('--scroll-progress', progress.toString());
        };

        mainEl.addEventListener('scroll', handleScroll);
        return () => mainEl.removeEventListener('scroll', handleScroll);
    }, []);

    return (
        <div className='tea-page'>
            <header className='tea-page-header'>
                {!hideBackButton && (
                    <button className='tea-page-back' onClick={() => navigate(backPath)} aria-label='Go back'>
                        <ArrowIcon />
                    </button>
                )}

                <div className='tea-page-header-content'>
                    {props.appName && <p className='tea-page-flare'>{props.appName}</p>}
                    <div className='tea-page-title-row'>
                        <div className='tea-page-title-container'>
                            <h1 className={`tea-page-title${isInfoHovered ? ' tea-page-title--blurred' : ''}`}>
                                {props.title}
                            </h1>
                            {props.tags && isInfoHovered && (
                                <div className='tea-page-tags-overlay'>
                                    <TeaTags tags={props.tags} />
                                </div>
                            )}
                        </div>
                        {props.description && (
                            <div
                                className='tea-page-infotip-wrapper'
                                onMouseEnter={() => setIsInfoHovered(true)}
                                onMouseLeave={() => setIsInfoHovered(false)}
                            >
                                <TeaInfotip position='right'>{props.description}</TeaInfotip>
                            </div>
                        )}
                    </div>
                </div>
            </header>

            <main ref={mainRef} className={`tea-page-main${scrollProgress > 0 ? ' tea-page-main--scrolled' : ''}`}>
                {props.children}
            </main>
        </div>
    );
};

export default TeaPage;

export { TeaPage };
