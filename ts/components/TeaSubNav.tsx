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

import React, { useState, useRef, useEffect } from 'react';

// Style
import './style/TeaSubNav.scss';

export interface TeaSubNavItem {
    /** Unique identifier for the tab */
    id: string;
    /** Display label for the tab */
    label: string;
    /** Optional icon to display next to the label when selected */
    icon?: React.ReactNode;
    /** Whether this tab is disabled */
    disabled?: boolean;
}

export interface TeaSubNavProps {
    /** Array of navigation items */
    items: TeaSubNavItem[];
    /** Currently selected item ID */
    selectedId: string;
    /** Callback when a tab is selected */
    onSelect: (id: string) => void;
    /** Additional CSS class */
    className?: string;
}

/**
 * TeaSubNav - A tab-style subnavigation component
 *
 * Features:
 * - Hover effect: draws a line under all tabs that extends to the end
 * - The hovered tab section is highlighted in a different color
 * - Selected tab is slightly elevated with permanent bottom border
 * - Optional icon appears next to selected tab label
 *
 * @example
 * ```tsx
 * const [activeTab, setActiveTab] = useState('overview');
 *
 * <TeaSubNav
 *     items={[
 *         { id: 'overview', label: 'Overview', icon: <HomeIcon /> },
 *         { id: 'details', label: 'Details' },
 *         { id: 'settings', label: 'Settings', icon: <GearIcon /> },
 *     ]}
 *     selectedId={activeTab}
 *     onSelect={setActiveTab}
 * />
 * ```
 */
export const TeaSubNav: React.FC<TeaSubNavProps> = ({ items, selectedId, onSelect, className = '' }) => {
    const [hoveredId, setHoveredId] = useState<string | null>(null);
    const [hoveredRect, setHoveredRect] = useState<{ left: number; width: number } | null>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const tabRefs = useRef<Map<string, HTMLButtonElement>>(new Map());

    // Update hover position when hovering
    useEffect(() => {
        if (hoveredId && containerRef.current) {
            const tabEl = tabRefs.current.get(hoveredId);
            if (tabEl) {
                const containerRect = containerRef.current.getBoundingClientRect();
                const tabRect = tabEl.getBoundingClientRect();
                setHoveredRect({
                    left: tabRect.left - containerRect.left,
                    width: tabRect.width,
                });
            }
        } else {
            setHoveredRect(null);
        }
    }, [hoveredId]);

    const handleTabClick = (item: TeaSubNavItem) => {
        if (!item.disabled) {
            onSelect(item.id);
        }
    };

    const setTabRef = (id: string) => (el: HTMLButtonElement | null) => {
        if (el) {
            tabRefs.current.set(id, el);
        } else {
            tabRefs.current.delete(id);
        }
    };

    return (
        <nav
            ref={containerRef}
            className={`tea-subnav${className ? ` ${className}` : ''}`}
            onMouseLeave={() => setHoveredId(null)}
        >
            <div className='tea-subnav__tabs'>
                {items.map((item) => {
                    const isSelected = item.id === selectedId;
                    const isHovered = item.id === hoveredId;

                    return (
                        <button
                            key={item.id}
                            ref={setTabRef(item.id)}
                            className={`tea-subnav__tab${isSelected ? ' tea-subnav__tab--selected' : ''}${isHovered ? ' tea-subnav__tab--hovered' : ''}${item.disabled ? ' tea-subnav__tab--disabled' : ''}`}
                            onClick={() => handleTabClick(item)}
                            onMouseEnter={() => setHoveredId(item.id)}
                            disabled={item.disabled}
                            aria-selected={isSelected}
                            role='tab'
                        >
                            {isSelected && item.icon && <span className='tea-subnav__tab-icon'>{item.icon}</span>}
                            <span className='tea-subnav__tab-label'>{item.label}</span>
                        </button>
                    );
                })}
            </div>

            {/* Bottom line container */}
            <div className='tea-subnav__line-container'>
                {/* Base line (appears on hover, extends full width) */}
                <div className={`tea-subnav__line-base${hoveredId ? ' tea-subnav__line-base--visible' : ''}`} />

                {/* Highlighted section under hovered tab */}
                {hoveredRect && (
                    <div
                        className='tea-subnav__line-highlight'
                        style={{
                            left: hoveredRect.left,
                            width: hoveredRect.width,
                        }}
                    />
                )}
            </div>
        </nav>
    );
};

export default TeaSubNav;
