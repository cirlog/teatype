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

// Style
import './style/TeaTooltip.scss';

type tTooltipPosition = 'top' | 'bottom' | 'left' | 'right';

interface iTeaTooltipProps {
    children: React.ReactNode;
    position?: tTooltipPosition;
    trigger: React.ReactNode;
}

const TeaTooltip: React.FC<iTeaTooltipProps> = (props) => {
    const position = props.position || 'top';

    return (
        <div className={`tea-tooltip tea-tooltip--${position}`}>
            <div className='tea-tooltip__trigger'>{props.trigger}</div>
            <div className='tea-tooltip__content'>{props.children}</div>
        </div>
    );
};

export default TeaTooltip;

export { TeaTooltip };

export type { tTooltipPosition };
