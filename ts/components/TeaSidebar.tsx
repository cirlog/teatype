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
import React, { useState, createContext, useContext } from 'react';

// Style
import './style/TeaSidebar.scss';

// ============================================================================
// Types
// ============================================================================

export interface iTeaSidebarItem {
    /** Unique identifier */
    id: string;
    /** Display title */
    title: string;
    /** Optional subtitle or preview text */
    subtitle?: string;
    /** Optional metadata (e.g., date, count) */
    meta?: string;
    /** Optional icon or emoji */
    icon?: React.ReactNode;
    /** Whether item is currently active/selected */
    active?: boolean;
}

export interface iTeaSidebarSection {
    /** Section identifier */
    id: string;
    /** Section title */
    title: string;
    /** Section items */
    items: iTeaSidebarItem[];
    /** Item count badge */
    count?: number;
    /** Whether section is collapsible */
    collapsible?: boolean;
    /** Default collapsed state */
    defaultCollapsed?: boolean;
}

export interface iTeaSidebarAction {
    /** Action identifier */
    id: string;
    /** Button label */
    label: string;
    /** Optional icon */
    icon?: React.ReactNode;
    /** Click handler */
    onClick: () => void;
    /** Button variant */
    variant?: 'primary' | 'secondary' | 'danger';
}

export interface iTeaSidebarProps {
    /** Sidebar title when expanded */
    title?: string;
    /** Whether sidebar is expanded */
    expanded: boolean;
    /** Toggle expansion callback */
    onToggle: () => void;
    /** Header actions (shown next to title) */
    headerActions?: iTeaSidebarAction[];
    /** Sidebar sections with items */
    sections?: iTeaSidebarSection[];
    /** Callback when an item is clicked */
    onItemClick?: (sectionId: string, itemId: string) => void;
    /** Callback when an item delete button is clicked */
    onItemDelete?: (sectionId: string, itemId: string) => void;
    /** Whether to show delete buttons on items */
    showItemDelete?: boolean;
    /** Footer content (settings panel, actions, etc.) */
    footer?: React.ReactNode;
    /** Custom content to render instead of default sections */
    children?: React.ReactNode;
    /** Width when expanded (default: 300px) */
    expandedWidth?: number;
    /** Width when collapsed (default: 50px) */
    collapsedWidth?: number;
    /** Empty state message when no items */
    emptyMessage?: string;
}

// ============================================================================
// Context for sidebar state
// ============================================================================

interface iTeaSidebarContextValue {
    expanded: boolean;
    onToggle: () => void;
}

const TeaSidebarContext = createContext<iTeaSidebarContextValue | null>(null);

export const useTeaSidebar = () => {
    const context = useContext(TeaSidebarContext);
    if (!context) {
        throw new Error('useTeaSidebar must be used within TeaSidebar');
    }
    return context;
};

// ============================================================================
// Sub-components
// ============================================================================

interface iTeaSidebarSectionComponentProps {
    section: iTeaSidebarSection;
    onItemClick?: (itemId: string) => void;
    onItemDelete?: (itemId: string) => void;
    showItemDelete?: boolean;
}

const TeaSidebarSectionComponent: React.FC<iTeaSidebarSectionComponentProps> = ({
    section,
    onItemClick,
    onItemDelete,
    showItemDelete,
}) => {
    const [collapsed, setCollapsed] = useState(section.defaultCollapsed ?? false);

    return (
        <div className='tea-sidebar-section'>
            <div
                className={`tea-sidebar-section__header ${section.collapsible ? 'tea-sidebar-section__header--collapsible' : ''}`}
                onClick={() => section.collapsible && setCollapsed(!collapsed)}
            >
                <span className='tea-sidebar-section__title'>{section.title}</span>
                {section.count !== undefined && <span className='tea-sidebar-section__count'>{section.count}</span>}
                {section.collapsible && (
                    <span
                        className={`tea-sidebar-section__chevron ${collapsed ? '' : 'tea-sidebar-section__chevron--open'}`}
                    >
                        ▶
                    </span>
                )}
            </div>

            {!collapsed && (
                <div className='tea-sidebar-section__items'>
                    {section.items.length === 0 ? (
                        <div className='tea-sidebar-section__empty'>No items</div>
                    ) : (
                        section.items.map((item) => (
                            <div
                                key={item.id}
                                className={`tea-sidebar-item ${item.active ? 'tea-sidebar-item--active' : ''}`}
                                onClick={() => onItemClick?.(item.id)}
                                role='button'
                                tabIndex={0}
                                onKeyDown={(e) => e.key === 'Enter' && onItemClick?.(item.id)}
                            >
                                {item.icon && <span className='tea-sidebar-item__icon'>{item.icon}</span>}
                                <div className='tea-sidebar-item__content'>
                                    <div className='tea-sidebar-item__header'>
                                        <span className='tea-sidebar-item__title'>{item.title}</span>
                                        {showItemDelete && onItemDelete && (
                                            <button
                                                className='tea-sidebar-item__delete'
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    onItemDelete(item.id);
                                                }}
                                                title='Delete'
                                            >
                                                ×
                                            </button>
                                        )}
                                    </div>
                                    {(item.subtitle || item.meta) && (
                                        <div className='tea-sidebar-item__meta'>
                                            {item.meta && <span className='tea-sidebar-item__date'>{item.meta}</span>}
                                            {item.subtitle && (
                                                <span className='tea-sidebar-item__subtitle'>{item.subtitle}</span>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}
        </div>
    );
};

// ============================================================================
// Settings Panel Sub-components
// ============================================================================

export interface iTeaSidebarSettingsSection {
    id: string;
    label: string;
    children: React.ReactNode;
}

export interface iTeaSidebarSettingsProps {
    isOpen: boolean;
    isClosing?: boolean;
    sections: iTeaSidebarSettingsSection[];
}

export const TeaSidebarSettings: React.FC<iTeaSidebarSettingsProps> = ({ isOpen, isClosing, sections }) => {
    if (!isOpen) return null;

    return (
        <div className={`tea-sidebar-settings ${isClosing ? 'tea-sidebar-settings--closing' : ''}`}>
            {sections.map((section) => (
                <div key={section.id} className='tea-sidebar-settings__section'>
                    <span className='tea-sidebar-settings__label'>{section.label}</span>
                    {section.children}
                </div>
            ))}
        </div>
    );
};

// ============================================================================
// Helper Components
// ============================================================================

export const TeaSidebarSlider: React.FC<{
    min: number;
    max: number;
    step?: number;
    value: number;
    onChange: (value: number) => void;
    unit?: string;
}> = ({ min, max, step = 1, value, onChange, unit = '' }) => (
    <div className='tea-sidebar-slider'>
        <input
            type='range'
            min={min}
            max={max}
            step={step}
            value={value}
            onChange={(e) => onChange(Number(e.target.value))}
        />
        <span className='tea-sidebar-slider__value'>
            {value}
            {unit}
        </span>
    </div>
);

export const TeaSidebarToggle: React.FC<{
    checked: boolean;
    onChange: (checked: boolean) => void;
    label: string;
}> = ({ checked, onChange, label }) => (
    <div className='tea-sidebar-toggle'>
        <label>
            <input type='checkbox' checked={checked} onChange={(e) => onChange(e.target.checked)} />
            {label}
        </label>
    </div>
);

export const TeaSidebarButton: React.FC<{
    onClick: () => void;
    variant?: 'default' | 'danger';
    children: React.ReactNode;
}> = ({ onClick, variant = 'default', children }) => (
    <button className={`tea-sidebar-btn tea-sidebar-btn--${variant}`} onClick={onClick}>
        {children}
    </button>
);

export const TeaSidebarButtonGroup: React.FC<{
    children: React.ReactNode;
}> = ({ children }) => <div className='tea-sidebar-btn-group'>{children}</div>;

// ============================================================================
// Main Component
// ============================================================================

export const TeaSidebar: React.FC<iTeaSidebarProps> = ({
    title,
    expanded,
    onToggle,
    headerActions,
    sections,
    onItemClick,
    onItemDelete,
    showItemDelete = true,
    footer,
    children,
    expandedWidth = 300,
    collapsedWidth = 50,
    emptyMessage = 'No items yet',
}) => {
    const contextValue: iTeaSidebarContextValue = {
        expanded,
        onToggle,
    };

    return (
        <TeaSidebarContext.Provider value={contextValue}>
            <aside
                className={`tea-sidebar ${expanded ? 'tea-sidebar--expanded' : 'tea-sidebar--collapsed'}`}
                style={
                    {
                        '--tea-sidebar-expanded-width': `${expandedWidth}px`,
                        '--tea-sidebar-collapsed-width': `${collapsedWidth}px`,
                    } as React.CSSProperties
                }
            >
                <div className='tea-sidebar__header'>
                    <button className='tea-sidebar__toggle' onClick={onToggle} title={expanded ? 'Collapse' : 'Expand'}>
                        <span className='tea-sidebar__toggle-icon'>{expanded ? '◀' : '▶'}</span>
                    </button>
                    {expanded && (
                        <>
                            {title && <h2 className='tea-sidebar__title'>{title}</h2>}
                            {headerActions?.map((action) => (
                                <button
                                    key={action.id}
                                    className={`tea-sidebar__action tea-sidebar__action--${action.variant || 'primary'}`}
                                    onClick={action.onClick}
                                    title={action.label}
                                >
                                    {action.icon || <span>+</span>}
                                </button>
                            ))}
                        </>
                    )}
                </div>

                {expanded && (
                    <>
                        <div className='tea-sidebar__content'>
                            {children ? (
                                children
                            ) : sections ? (
                                sections.map((section) => (
                                    <TeaSidebarSectionComponent
                                        key={section.id}
                                        section={section}
                                        onItemClick={(itemId) => onItemClick?.(section.id, itemId)}
                                        onItemDelete={(itemId) => onItemDelete?.(section.id, itemId)}
                                        showItemDelete={showItemDelete}
                                    />
                                ))
                            ) : (
                                <div className='tea-sidebar__empty'>{emptyMessage}</div>
                            )}
                        </div>

                        {footer && <div className='tea-sidebar__footer'>{footer}</div>}
                    </>
                )}
            </aside>
        </TeaSidebarContext.Provider>
    );
};

export default TeaSidebar;
