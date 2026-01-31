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
import React, { useEffect, useState, useRef, useCallback, createContext, useContext } from 'react';
import { createPortal } from 'react-dom';

// Style
import './style/TeaToast.scss';

// ============================================================================
// Types
// ============================================================================

export type tTeaToastType = 'success' | 'error' | 'info' | 'warning';
export type tTeaToastPosition =
    | 'top-left'
    | 'top-right'
    | 'bottom-left'
    | 'bottom-right'
    | 'top-center'
    | 'bottom-center';

export interface iTeaToastOptions {
    /** Toast type determines color and icon */
    type?: tTeaToastType;
    /** Duration in milliseconds (default: 5000, 0 = infinite) */
    duration?: number;
    /** Whether toast is dismissible by click (default: true) */
    dismissible?: boolean;
    /** Custom icon (overrides default type icon) */
    icon?: React.ReactNode;
    /** Action button */
    action?: {
        label: string;
        onClick: () => void;
    };
}

export interface iTeaToastItem extends iTeaToastOptions {
    id: string;
    message: string;
}

// ============================================================================
// Individual Toast Component
// ============================================================================

interface iTeaToastProps {
    toast: iTeaToastItem;
    onClose: () => void;
}

const TeaToastItem: React.FC<iTeaToastProps> = ({ toast, onClose }) => {
    const { message, type = 'info', duration = 5000, dismissible = true, icon, action } = toast;

    const [isClosing, setIsClosing] = useState(false);
    const [progress, setProgress] = useState(360); // degrees for conic gradient
    const animationRef = useRef<number | null>(null);
    const startTimeRef = useRef<number | null>(null);
    const isPausedRef = useRef(false);
    const remainingTimeRef = useRef(duration);

    // Progress animation with pause support
    useEffect(() => {
        if (duration === 0) return; // Infinite toast

        const animate = (timestamp: number) => {
            if (!startTimeRef.current) startTimeRef.current = timestamp;

            if (isPausedRef.current) {
                startTimeRef.current = timestamp - (duration - remainingTimeRef.current);
                animationRef.current = requestAnimationFrame(animate);
                return;
            }

            const elapsed = timestamp - startTimeRef.current;
            const remaining = Math.max(0, duration - elapsed);
            remainingTimeRef.current = remaining;
            const progressPercent = remaining / duration;
            setProgress(progressPercent * 360);

            if (remaining <= 0) {
                setIsClosing(true);
            } else {
                animationRef.current = requestAnimationFrame(animate);
            }
        };

        animationRef.current = requestAnimationFrame(animate);

        return () => {
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current);
            }
        };
    }, [duration]);

    // Handle closing animation
    useEffect(() => {
        if (isClosing) {
            const closeTimer = setTimeout(onClose, 300); // Match animation duration
            return () => clearTimeout(closeTimer);
        }
    }, [isClosing, onClose]);

    const handleClick = () => {
        if (dismissible) {
            setIsClosing(true);
        }
    };

    const handleMouseEnter = () => {
        isPausedRef.current = true;
    };

    const handleMouseLeave = () => {
        isPausedRef.current = false;
        startTimeRef.current = null;
    };

    const getIcon = () => {
        if (icon) return icon;
        switch (type) {
            case 'success':
                return '✓';
            case 'error':
                return '✕';
            case 'warning':
                return '⚠';
            case 'info':
            default:
                return 'ℹ';
        }
    };

    return (
        <div
            className={`tea-toast tea-toast--${type} ${isClosing ? 'tea-toast--closing' : ''}`}
            onClick={handleClick}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            style={
                {
                    '--tea-toast-duration': `${duration}ms`,
                    '--tea-toast-progress': `${progress}deg`,
                } as React.CSSProperties
            }
            role='alert'
        >
            <div className='tea-toast__border-timer' />
            <div className='tea-toast__content'>
                <span className='tea-toast__icon'>{getIcon()}</span>
                <span className='tea-toast__message'>{message}</span>
                {action && (
                    <button
                        className='tea-toast__action'
                        onClick={(e) => {
                            e.stopPropagation();
                            action.onClick();
                            setIsClosing(true);
                        }}
                    >
                        {action.label}
                    </button>
                )}
            </div>
        </div>
    );
};

// ============================================================================
// Toast Container Component
// ============================================================================

interface iTeaToastContainerProps {
    toasts: iTeaToastItem[];
    position?: tTeaToastPosition;
    onRemove: (id: string) => void;
}

export const TeaToastContainer: React.FC<iTeaToastContainerProps> = ({
    toasts,
    position = 'bottom-right',
    onRemove,
}) => {
    if (toasts.length === 0) return null;

    const container = (
        <div className={`tea-toast-container tea-toast-container--${position}`}>
            {toasts.map((toast) => (
                <TeaToastItem key={toast.id} toast={toast} onClose={() => onRemove(toast.id)} />
            ))}
        </div>
    );

    return createPortal(container, document.body);
};

// ============================================================================
// Toast Hook
// ============================================================================

export interface iUseTeaToastReturn {
    /** Current toast position */
    position: tTeaToastPosition;
    /** All active toasts */
    toasts: iTeaToastItem[];

    /** Add a toast with custom options */
    addToast: (message: string, options?: iTeaToastOptions) => string;
    /** Remove all toasts */
    clearToasts: () => void;
    /** Shorthand for error toast */
    error: (message: string, options?: Omit<iTeaToastOptions, 'type'>) => string;
    /** Shorthand for info toast */
    info: (message: string, options?: Omit<iTeaToastOptions, 'type'>) => string;
    /** Remove a specific toast */
    removeToast: (id: string) => void;
    /** Shorthand for success toast */
    success: (message: string, options?: Omit<iTeaToastOptions, 'type'>) => string;
    /** Shorthand for warning toast */
    warning: (message: string, options?: Omit<iTeaToastOptions, 'type'>) => string;
}

export const useTeaToast = (defaultPosition: tTeaToastPosition = 'bottom-right'): iUseTeaToastReturn => {
    const [toasts, setToasts] = useState<iTeaToastItem[]>([]);
    const [position] = useState<tTeaToastPosition>(defaultPosition);

    const generateId = () => `tea-toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    const addToast = useCallback((message: string, options: iTeaToastOptions = {}): string => {
        const id = generateId();
        const newToast: iTeaToastItem = {
            id,
            message,
            type: options.type || 'info',
            duration: options.duration ?? 5000,
            dismissible: options.dismissible ?? true,
            icon: options.icon,
            action: options.action,
        };
        setToasts((prev) => [...prev, newToast]);
        return id;
    }, []);

    const removeToast = useCallback((id: string) => {
        setToasts((prev) => prev.filter((toast) => toast.id !== id));
    }, []);

    const clearToasts = useCallback(() => {
        setToasts([]);
    }, []);

    const success = useCallback(
        (message: string, options?: Omit<iTeaToastOptions, 'type'>) => {
            return addToast(message, { ...options, type: 'success' });
        },
        [addToast],
    );

    const error = useCallback(
        (message: string, options?: Omit<iTeaToastOptions, 'type'>) => {
            return addToast(message, { ...options, type: 'error' });
        },
        [addToast],
    );

    const warning = useCallback(
        (message: string, options?: Omit<iTeaToastOptions, 'type'>) => {
            return addToast(message, { ...options, type: 'warning' });
        },
        [addToast],
    );

    const info = useCallback(
        (message: string, options?: Omit<iTeaToastOptions, 'type'>) => {
            return addToast(message, { ...options, type: 'info' });
        },
        [addToast],
    );

    return {
        toasts,
        position,
        addToast,
        removeToast,
        clearToasts,
        success,
        error,
        warning,
        info,
    };
};

// ============================================================================
// Toast Context (for app-wide toast access)
// ============================================================================

const TeaToastContext = createContext<iUseTeaToastReturn | null>(null);

export const useTeaToastContext = (): iUseTeaToastReturn => {
    const context = useContext(TeaToastContext);
    if (!context) {
        throw new Error('useTeaToastContext must be used within TeaToastProvider');
    }
    return context;
};

interface iTeaToastProviderProps {
    children: React.ReactNode;
    position?: tTeaToastPosition;
}

export const TeaToastProvider: React.FC<iTeaToastProviderProps> = ({ children, position = 'bottom-right' }) => {
    const toast = useTeaToast(position);

    return (
        <TeaToastContext.Provider value={toast}>
            {children}
            <TeaToastContainer toasts={toast.toasts} position={toast.position} onRemove={toast.removeToast} />
        </TeaToastContext.Provider>
    );
};

// ============================================================================
// Export
// ============================================================================

export default TeaToastContainer;
