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
import React, { createContext, useContext } from 'react';

// Hooks
import useStatusPulse, { tStatusSnapshot } from '../hooks/useStatusPulse';

interface iDashboardContextValue {
    error: string | null;
    history: string[];
    status: tStatusSnapshot;
    updating: boolean;

    refresh: () => Promise<void>;
}

const DashboardContext = createContext<iDashboardContextValue | null>(null);

/**
 * Hook to access the dashboard context.
 * Must be used within a DashboardProvider.
 */
export const useDashboard = (): iDashboardContextValue => {
    const context = useContext(DashboardContext);
    if (!context) {
        throw new Error('useDashboard must be used within a DashboardProvider');
    }
    return context;
};

interface iDashboardProviderProps {
    children: React.ReactNode;
    /** Optional custom status endpoint */
    endpoint?: string;
}

/**
 * Provider component that wraps children with dashboard state.
 * The status pulse (polling) is kept alive as long as this provider is mounted.
 */
export const DashboardProvider: React.FC<iDashboardProviderProps> = ({ children, endpoint }) => {
    const dashboardState = useStatusPulse(endpoint);

    return <DashboardContext.Provider value={dashboardState}>{children}</DashboardContext.Provider>;
};

export default DashboardContext;
