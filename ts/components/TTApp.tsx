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

import { BrowserRouter } from 'react-router-dom';

// Style
import './style/TTApp.scss';

export interface iPageInfo {
    path: string;
    title: string;
    description?: string;
    icon?: React.ReactNode;
}

interface iTTAppProps {
    children: React.ReactNode;
    name: string;
}

const TTApp: React.FC<iTTAppProps> = ({ children, name }) => {
    return (
        <BrowserRouter>
            <div id='tt-app' data-app-name={name}>
                {children}
            </div>
        </BrowserRouter>
    );
};

export default TTApp;

export { TTApp };
