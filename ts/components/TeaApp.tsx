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
import { BrowserRouter } from 'react-router-dom';

// Style
import './style/TeaApp.scss';

interface iPage {
    content?: React.FC;
    longDescription?: string;
    path: string;
    shortDescription?: string;
    tags?: string[];
    title: string;
}

interface iTeaAppProps {
    children: React.ReactNode;
    name: string;
}

const TeaApp: React.FC<iTeaAppProps> = (props) => {
    return (
        <BrowserRouter>
            <div id='tea-app' data-app-name={props.name}>
                {props.children}
            </div>
        </BrowserRouter>
    );
};

export default TeaApp;

export { TeaApp };

export type { iPage };
