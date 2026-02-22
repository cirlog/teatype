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
import React, { useRef, useState, useCallback, useEffect, useMemo } from 'react';

// Style
import './style/TeaSlider.scss';

type tSliderSize = 'small' | 'medium' | 'large';
type tSliderTheme = 'default' | 'accent';

interface iTeaSliderProps {
    /** Current value */
    value: number;
    /** Change handler */
    onChange: (value: number) => void;
    /** Minimum value (default: 0) */
    min?: number;
    /** Maximum value (default: 100) */
    max?: number;
    /** Step increment (default: 1) */
    step?: number;
    /** Show thin tick marks at every step position (default: false) */
    marks?: boolean;
    /** Show the current value label (default: true) */
    showValue?: boolean;
    /** Format function for the displayed value */
    formatValue?: (value: number) => string;
    /** Label text */
    label?: string;
    /** Hint text below the slider */
    hint?: string;
    /** Size variant */
    size?: tSliderSize;
    /** Theme variant */
    theme?: tSliderTheme;
    /** Disabled state */
    disabled?: boolean;
    /** Additional class */
    className?: string;
}

const TeaSlider: React.FC<iTeaSliderProps> = ({
    value,
    onChange,
    min = 0,
    max = 100,
    step = 1,
    marks = false,
    showValue = true,
    formatValue,
    label,
    hint,
    size = 'medium',
    theme = 'default',
    disabled = false,
    className = '',
}) => {
    const trackRef = useRef<HTMLDivElement>(null);
    const [isDragging, setIsDragging] = useState(false);
    const [isHovering, setIsHovering] = useState(false);

    /** Calculate percentage of current value within range */
    const percentage = useMemo(() => {
        return ((value - min) / (max - min)) * 100;
    }, [value, min, max]);

    /** Snap a raw numeric value to the nearest step */
    const snapToStep = useCallback(
        (raw: number): number => {
            const clamped = Math.min(max, Math.max(min, raw));
            const steps = Math.round((clamped - min) / step);
            return min + steps * step;
        },
        [min, max, step],
    );

    /** Resolve a pointer event to a snapped value and fire onChange */
    const resolveValue = useCallback(
        (clientX: number) => {
            const track = trackRef.current;
            if (!track) return;

            const rect = track.getBoundingClientRect();
            const ratio = Math.min(1, Math.max(0, (clientX - rect.left) / rect.width));
            const raw = min + ratio * (max - min);
            const snapped = snapToStep(raw);

            if (snapped !== value) {
                onChange(snapped);
            }
        },
        [min, max, snapToStep, onChange, value],
    );

    /** Mouse / touch handlers */
    const handlePointerDown = useCallback(
        (e: React.PointerEvent) => {
            if (disabled) return;
            e.preventDefault();
            (e.target as HTMLElement).setPointerCapture(e.pointerId);
            setIsDragging(true);
            resolveValue(e.clientX);
        },
        [disabled, resolveValue],
    );

    const handlePointerMove = useCallback(
        (e: React.PointerEvent) => {
            if (!isDragging) return;
            resolveValue(e.clientX);
        },
        [isDragging, resolveValue],
    );

    const handlePointerUp = useCallback(() => {
        setIsDragging(false);
    }, []);

    /** Keyboard support */
    const handleKeyDown = useCallback(
        (e: React.KeyboardEvent) => {
            if (disabled) return;
            let newValue = value;
            switch (e.key) {
                case 'ArrowRight':
                case 'ArrowUp':
                    newValue = Math.min(max, value + step);
                    break;
                case 'ArrowLeft':
                case 'ArrowDown':
                    newValue = Math.max(min, value - step);
                    break;
                case 'Home':
                    newValue = min;
                    break;
                case 'End':
                    newValue = max;
                    break;
                default:
                    return;
            }
            e.preventDefault();
            onChange(newValue);
        },
        [disabled, value, min, max, step, onChange],
    );

    /** Compute mark positions as percentages */
    const markPositions = useMemo(() => {
        if (!marks) return [];
        const positions: number[] = [];
        for (let v = min; v <= max; v += step) {
            positions.push(((v - min) / (max - min)) * 100);
        }
        return positions;
    }, [marks, min, max, step]);

    const displayValue = formatValue ? formatValue(value) : String(value);

    const rootClasses = [
        'tea-slider',
        `size-${size}`,
        `theme-${theme}`,
        isDragging && 'dragging',
        isHovering && 'hovering',
        disabled && 'disabled',
        className,
    ]
        .filter(Boolean)
        .join(' ');

    return (
        <div className={rootClasses}>
            {label && <label className='tea-slider__label'>{label}</label>}

            <div className='tea-slider__row'>
                <div
                    ref={trackRef}
                    className='tea-slider__track-wrapper'
                    onPointerDown={handlePointerDown}
                    onPointerMove={handlePointerMove}
                    onPointerUp={handlePointerUp}
                    onPointerCancel={handlePointerUp}
                    onMouseEnter={() => setIsHovering(true)}
                    onMouseLeave={() => setIsHovering(false)}
                    role='slider'
                    aria-valuemin={min}
                    aria-valuemax={max}
                    aria-valuenow={value}
                    aria-disabled={disabled}
                    tabIndex={disabled ? -1 : 0}
                    onKeyDown={handleKeyDown}
                >
                    {/* Background track */}
                    <div className='tea-slider__track'>
                        {/* Filled portion */}
                        <div className='tea-slider__fill' style={{ width: `${percentage}%` }} />
                    </div>

                    {/* Step marks */}
                    {marks && (
                        <div className='tea-slider__marks'>
                            {markPositions.map((pos, i) => (
                                <span
                                    key={i}
                                    className={`tea-slider__mark ${pos <= percentage ? 'tea-slider__mark--active' : ''}`}
                                    style={{ left: `${pos}%` }}
                                />
                            ))}
                        </div>
                    )}

                    {/* Thumb */}
                    <div className='tea-slider__thumb-container' style={{ left: `${percentage}%` }}>
                        {/* Focus / drag ring (Material-UI style) */}
                        <div className='tea-slider__thumb-ring' />
                        <div className='tea-slider__thumb' />
                    </div>
                </div>

                {showValue && <span className='tea-slider__value'>{displayValue}</span>}
            </div>

            {hint && <p className='tea-slider__hint'>{hint}</p>}
        </div>
    );
};

export default TeaSlider;

export { TeaSlider };
export type { iTeaSliderProps, tSliderSize, tSliderTheme };
