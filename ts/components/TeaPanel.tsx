/**
 * @license
 * Copyright (c) 2024-2025 enamentis GmbH. All rights reserved.
 *
 * This software module is the proprietary property of enamentis GmbH.
 * Unauthorized copying, modification, distribution, or use of this software
 * is strictly prohibited unless explicitly authorized in writing.
 *
 * THIS SOFTWARE IS PROVIDED "AS IS," WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NONINFRINGEMENT.
 * IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
 * DAMAGES, OR OTHER LIABILITY ARISING FROM THE USE OF THIS SOFTWARE.
 *
 * For more details, check the LICENSE file in the root directory of this repository.
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
    const className = [
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
        <div className={className}>
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
