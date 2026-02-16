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
import React, { useState, useRef, useEffect } from 'react';
import { NavLink, Routes, Route, useLocation, useNavigate } from 'react-router-dom';

// Style
import './style/TeaSubNav.scss';

export interface iTeaSubNavItem {
    /** Unique identifier for the tab */
    id: string;
    /** Display label for the tab */
    label: string;
    /** Route path for navigation (when using routing mode) */
    path?: string;
    /** Component to render when this tab is active (when using routing mode) */
    component?: React.ComponentType;
    /** Optional icon to display next to the label when selected */
    icon?: React.ReactNode;
    /** Whether this tab is disabled */
    disabled?: boolean;
}

export interface iTeaSubNavProps {
    /** Array of navigation items */
    items: iTeaSubNavItem[];
    /** Currently selected item ID (only used when not using routing mode) */
    selectedId?: string;
    /** Callback when a tab is selected (only used when not using routing mode) */
    onSelect?: (id: string) => void;
    /** Additional CSS class */
    className?: string;
    /** Base path for relative routing (defaults to current location) */
    basePath?: string;
    /** Whether to render Routes for the components (default: true if items have paths) */
    renderRoutes?: boolean;
}

const TeaSubNav: React.FC<iTeaSubNavProps> = ({
    items,
    selectedId,
    onSelect,
    className = '',
    basePath,
    renderRoutes = true,
}) => {
    const [hoveredId, setHoveredId] = useState<string | null>(null);
    const [hoveredRect, setHoveredRect] = useState<{ left: number; width: number } | null>(null);
    const tabsRef = useRef<HTMLDivElement>(null);
    const tabRefs = useRef<Map<string, HTMLElement>>(new Map());
    const location = useLocation();
    const navigate = useNavigate();

    // Determine if we're in routing mode (items have paths)
    const isRoutingMode = items.some((item) => item.path !== undefined);

    // Resolve the base path
    const resolvedBasePath = basePath ?? '';

    // Get the full path for an item
    const getItemPath = (item: iTeaSubNavItem): string => {
        if (!item.path) return '';
        const base = resolvedBasePath.endsWith('/') ? resolvedBasePath.slice(0, -1) : resolvedBasePath;
        const path = item.path.startsWith('/') ? item.path : `/${item.path}`;
        return `${base}${path}`;
    };

    // Determine the active item based on current location (for routing mode)
    const getActiveItemId = (): string | undefined => {
        if (!isRoutingMode) return selectedId;

        // Find the item whose path matches the current location
        for (const item of items) {
            if (item.path) {
                const itemPath = getItemPath(item);
                if (location.pathname === itemPath || location.pathname.startsWith(`${itemPath}/`)) {
                    return item.id;
                }
            }
        }

        // Default to first non-disabled item
        return items.find((item) => !item.disabled)?.id;
    };

    const activeItemId = getActiveItemId();

    // Redirect to first non-disabled tab when on base path (routing mode only)
    useEffect(() => {
        if (!isRoutingMode) return;

        const normalizedBasePath = resolvedBasePath.endsWith('/') ? resolvedBasePath.slice(0, -1) : resolvedBasePath;

        // Check if we're on the base path (exactly or with trailing slash)
        if (location.pathname === normalizedBasePath || location.pathname === `${normalizedBasePath}/`) {
            const firstEnabledItem = items.find((item) => item.path && !item.disabled);
            if (firstEnabledItem) {
                navigate(getItemPath(firstEnabledItem), { replace: true });
            }
        }
    }, [location.pathname, isRoutingMode, resolvedBasePath, items, navigate]);

    // Update hover position when hovering
    useEffect(() => {
        if (hoveredId && tabsRef.current) {
            const tabEl = tabRefs.current.get(hoveredId);
            if (tabEl) {
                const tabsRect = tabsRef.current.getBoundingClientRect();
                const tabRect = tabEl.getBoundingClientRect();
                setHoveredRect({
                    left: tabRect.left - tabsRect.left,
                    width: tabRect.width,
                });
            }
        } else {
            setHoveredRect(null);
        }
    }, [hoveredId]);

    const handleTabClick = (item: iTeaSubNavItem) => {
        if (item.disabled) return;

        if (isRoutingMode && item.path) {
            navigate(getItemPath(item));
        } else if (onSelect) {
            onSelect(item.id);
        }
    };

    const setTabRef = (id: string) => (el: HTMLElement | null) => {
        if (el) {
            tabRefs.current.set(id, el);
        } else {
            tabRefs.current.delete(id);
        }
    };

    // Render a tab element (either NavLink or button)
    const renderTab = (item: iTeaSubNavItem) => {
        const isSelected = item.id === activeItemId;
        const isHovered = item.id === hoveredId;

        const tabClassName = `tea-subnav__tab${isSelected ? ' tea-subnav__tab--selected' : ''}${isHovered ? ' tea-subnav__tab--hovered' : ''}${item.disabled ? ' tea-subnav__tab--disabled' : ''}`;

        const tabContent = (
            <>
                {item.icon && <span className='tea-subnav__tab-icon'>{item.icon}</span>}
                <span className='tea-subnav__tab-label'>{item.label}</span>
            </>
        );

        if (isRoutingMode && item.path && !item.disabled) {
            return (
                <NavLink
                    key={item.id}
                    ref={setTabRef(item.id) as React.Ref<HTMLAnchorElement>}
                    to={getItemPath(item)}
                    className={tabClassName}
                    onMouseEnter={() => setHoveredId(item.id)}
                    aria-selected={isSelected}
                    role='tab'
                >
                    {tabContent}
                </NavLink>
            );
        }

        return (
            <button
                key={item.id}
                ref={setTabRef(item.id) as React.Ref<HTMLButtonElement>}
                className={tabClassName}
                onClick={() => handleTabClick(item)}
                onMouseEnter={() => setHoveredId(item.id)}
                disabled={item.disabled}
                aria-selected={isSelected}
                role='tab'
            >
                {tabContent}
            </button>
        );
    };

    // Render routes for components (only in routing mode)
    const renderComponentRoutes = () => {
        if (!isRoutingMode || !renderRoutes) return null;

        const itemsWithComponents = items.filter((item) => item.path && item.component);
        if (itemsWithComponents.length === 0) return null;

        return (
            <div className='tea-subnav__content'>
                <Routes>
                    {itemsWithComponents.map((item) => {
                        const Component = item.component!;
                        const relativePath = item.path!.startsWith('/') ? item.path!.slice(1) : item.path!;
                        return <Route key={item.id} path={relativePath} element={<Component />} />;
                    })}
                </Routes>
            </div>
        );
    };

    return (
        <div className={`tea-subnav-container${className ? ` ${className}` : ''}`}>
            <nav className='tea-subnav' onMouseLeave={() => setHoveredId(null)}>
                <div ref={tabsRef} className='tea-subnav__tabs'>
                    {items.map(renderTab)}
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
            {renderComponentRoutes()}
        </div>
    );
};

export default TeaSubNav;

export { TeaSubNav };
