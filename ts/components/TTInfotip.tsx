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
import { TTTooltip } from './TTTooltip';

// Style
import './style/TTInfotip.scss';

type TooltipPosition = 'top' | 'bottom' | 'left' | 'right';

interface iTTInfotipProps {
    children: React.ReactNode;
    position?: TooltipPosition;
    trigger: React.ReactNode;
}

const TTInfotip: React.FC<iTTInfotipProps> = ({ children, content, position = 'right' }) => {
    return <TTTooltip position='right'>{props.children}</TTTooltip>;
};

export default TTInfotip;

export { TTInfotip };

export type { TooltipPosition };
