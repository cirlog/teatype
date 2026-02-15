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
import React from 'react';

// Style
import './style/TeaButton.scss';

type tButtonSize = 'small' | 'medium' | 'large';
type tButtonTheme = 'default' | 'filled' | 'success' | 'danger' | 'ghost';
type tButtonVariant = 'default';

interface iTeaButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    children?: React.ReactNode;
    icon?: React.ReactNode;
    iconPosition?: 'left' | 'right';
    loading?: boolean;
    size?: tButtonSize;
    theme?: tButtonTheme;
    variant?: tButtonVariant;
}

const TeaButton: React.FC<iTeaButtonProps> = (props) => {
    // Default props
    const iconPosition = props.iconPosition ?? 'left';
    const loading = props.loading ?? false;
    const size = props.size ?? 'medium';
    const theme = props.theme ?? 'default';
    const variant = props.variant ?? 'default';

    // Constants
    const classes = [
        'tea-button',
        `size-${size}`,
        `theme-${theme}`,
        `variant-${variant}`,
        loading && 'loading',
        props.className ?? '',
    ]
        .filter(Boolean)
        .join(' ');

    return (
        <button className={classes} disabled={props.disabled || loading} {...props}>
            {loading && (
                <span className='spinner'>
                    <svg viewBox='0 0 24 24' fill='none' stroke='currentColor' strokeWidth='2'>
                        <circle cx='12' cy='12' r='10' opacity='0.25' />
                        <path d='M12 2a10 10 0 0 1 10 10' />
                    </svg>
                </span>
            )}

            {props.icon && iconPosition === 'left' && !loading && <span className='icon'>{props.icon}</span>}

            {props.children && <span className='text'>{props.children}</span>}

            {props.icon && iconPosition === 'right' && !loading && <span className='icon'>{props.icon}</span>}
        </button>
    );
};

export default TeaButton;

export { TeaButton };
