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
import React, { createContext, useContext, useState, useCallback } from 'react';

// Components
import { TeaButton } from './TeaInput/TeaButton';
import { TeaModal } from './TeaModal';

// Style
import './style/TeaConfirm.scss';

interface ConfirmOptions {
    title?: string;
    message: string;
    confirmText?: string;
    cancelText?: string;
    variant?: 'default' | 'danger';
}

interface ConfirmContextValue {
    confirm: (options: ConfirmOptions) => Promise<boolean>;
}

const ConfirmContext = createContext<ConfirmContextValue | null>(null);

interface ConfirmState extends ConfirmOptions {
    isOpen: boolean;
    resolve: ((value: boolean) => void) | null;
}

const TeaConfirmProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [state, setState] = useState<ConfirmState>({
        isOpen: false,
        message: '',
        resolve: null,
    });

    const confirm = useCallback((options: ConfirmOptions): Promise<boolean> => {
        return new Promise((resolve) => {
            setState({
                isOpen: true,
                ...options,
                resolve,
            });
        });
    }, []);

    const handleConfirm = () => {
        state.resolve?.(true);
        setState((prev) => ({ ...prev, isOpen: false, resolve: null }));
    };

    const handleCancel = () => {
        state.resolve?.(false);
        setState((prev) => ({ ...prev, isOpen: false, resolve: null }));
    };

    return (
        <ConfirmContext.Provider value={{ confirm }}>
            {children}
            <TeaModal
                isOpen={state.isOpen}
                onClose={handleCancel}
                title={state.title || 'Confirm'}
                size='sm'
                closeOnOverlayClick={false}
                footer={
                    <div className='tea-confirm__actions'>
                        <TeaButton variant='ghost' onClick={handleCancel}>
                            {state.cancelText || 'Cancel'}
                        </TeaButton>
                        <TeaButton variant={state.variant === 'danger' ? 'danger' : 'primary'} onClick={handleConfirm}>
                            {state.confirmText || 'Confirm'}
                        </TeaButton>
                    </div>
                }
            >
                <p className='tea-confirm__message'>{state.message}</p>
            </TeaModal>
        </ConfirmContext.Provider>
    );
};

const useConfirm = (): ((options: ConfirmOptions) => Promise<boolean>) => {
    const context = useContext(ConfirmContext);
    if (!context) {
        throw new Error('useConfirm must be used within a TeaConfirmProvider');
    }
    return context.confirm;
};

export default TeaConfirmProvider;

export { TeaConfirmProvider, useConfirm };
