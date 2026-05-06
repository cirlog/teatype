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
import { ReactElement } from 'react';

// Icons
import { RoundedSquareIcon } from '@teatype/icons';

// Style
import './style/TeaPanel.scss';

interface iTeaPanelProps {
    borderThickness?: 'thin' | 'medium' | 'thick';
    children: React.ReactNode;
    className?: string;
    id?: string;
    padding?: 'none' | 'small' | 'medium' | 'large';
    size?: 'dymnamic' | 'full';
    title?: string;
    useTheme?: boolean;
    variant?: 'card' | 'framed';
}

const TeaPanel: React.FC<iTeaPanelProps> = (props) => {
    const classes = [
        'tea-panel',
        props.className || '',
        props.padding ? `padding-${props.padding}` : 'padding-none',
        props.size ? `size-${props.size}` : 'size-dynamic',
        props.useTheme && 'use-theme',
        props.variant ? `variant-${props.variant}` : 'variant-default',
    ]
        .filter(Boolean)
        .join(' ');

    const wrapComponent = (content: ReactElement) => {
        if (props.variant === 'framed') {
            return <fieldset>{content}</fieldset>;
        }
        return content;
    };

    return (
        <div className={classes}>
            {wrapComponent(
                <>
                    {props.title && (
                        <legend className='title'>
                            {/* <RoundedSquareIcon /> */}

                            {props.title}
                        </legend>
                    )}

                    {props.children}
                </>,
            )}
        </div>
    );
};

export default TeaPanel;

export { TeaPanel };
