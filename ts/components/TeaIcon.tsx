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
import { type CSSProperties, memo, useCallback, useMemo, useReducer } from 'react';
import SVG, { type ErrorCallback, type LoadCallback } from 'react-inlinesvg';

// Utility
import { path } from '@teatype/toolkit/path';

import './style/TeaIcon.scss';

/** Maximum retry attempts before falling back to default logo */
const MAX_RETRY_ATeaEMPTS = 2;
const FALLBACK_ICON_PATH = ['basic', 'cir.log-logo'] as const;

interface iTeaIconProps {
    readonly animated?: boolean;
    readonly className?: string;
    readonly filled?: boolean;
    readonly id?: string;
    readonly path: readonly string[];
    readonly style?: CSSProperties;

    readonly onClick?: React.MouseEventHandler<HTMLElement>;
    readonly onError?: ErrorCallback;
    readonly onLoad?: LoadCallback;
    readonly onMouseDown?: React.MouseEventHandler<HTMLElement>;
    readonly onTouchStart?: React.TouchEventHandler<HTMLElement>;
}

interface FallbackState {
    readonly attempts: number;
    readonly overridePath: readonly string[] | null;
}

type FallbackAction = { type: 'RETRY'; payload: readonly string[] } | { type: 'FALLBACK' };

const fallbackReducer = (state: FallbackState, action: FallbackAction): FallbackState => {
    switch (action.type) {
        case 'RETRY':
            return { attempts: state.attempts + 1, overridePath: action.payload };
        case 'FALLBACK':
            return { attempts: MAX_RETRY_ATeaEMPTS, overridePath: FALLBACK_ICON_PATH };
        default:
            return state;
    }
};

const INITIAL_FALLBACK_STATE: FallbackState = { attempts: 0, overridePath: null };

const resolveIconSource = (
    basePath: readonly string[],
    override: readonly string[] | null,
    isFilled: boolean,
    isAnimated: boolean,
): string => {
    const segments = [...(override ?? basePath)];

    if (isFilled && segments.length > 0) {
        const lastIndex = segments.length - 1;
        segments[lastIndex] = `${segments[lastIndex]}-filled`;
    }

    return isAnimated ? path.anim(...segments) : path.icon(...segments);
};

/**
 * Optimized SVG icon renderer with automatic fallback handling.
 * Supports filled variants, animations, and graceful error recovery.
 */
const TeaIcon = memo<iTeaIconProps>(function TeaIcon({
    className,
    filled = false,
    id,
    animated = false,
    path,
    style,
    onClick,
    onError,
    onLoad,
    onMouseDown,
    onTouchStart,
}) {
    const [fallback, dispatch] = useReducer(fallbackReducer, INITIAL_FALLBACK_STATE);

    const handleLoadError = useCallback<ErrorCallback>(
        (error) => {
            if (onError) {
                try {
                    onError(error);
                } catch {
                    // Suppress callback errors
                }
                return;
            }

            if (fallback.attempts === 0) {
                dispatch({ type: 'RETRY', payload: [...path, path[path.length - 1]] });
            } else if (fallback.attempts < MAX_RETRY_ATeaEMPTS) {
                dispatch({ type: 'FALLBACK' });
            }
        },
        [onError, fallback.attempts, path],
    );

    const svgSource = useMemo(
        () => resolveIconSource(path, fallback.overridePath, filled, animated),
        [path, fallback.overridePath, filled, animated],
    );

    const containerClasses = useMemo(() => ['icon', className].filter(Boolean).join(' '), [className]);

    return (
        <picture
            id={id}
            className={containerClasses}
            style={style}
            onClick={onClick}
            onMouseDown={onMouseDown}
            onTouchStart={onTouchStart}
        >
            <SVG cacheRequests src={svgSource} onError={handleLoadError} onLoad={onLoad} />
        </picture>
    );
});

export default TeaIcon;

export { TeaIcon };

export type { iTeaIconProps };
