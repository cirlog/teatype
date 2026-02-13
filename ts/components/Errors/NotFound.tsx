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
import { useNavigate } from 'react-router-dom';

// Components
import { TeaButton } from '../TeaButton';

// Style
import './style/NotFound.scss';

/**
 * 404 page component shown when navigating to an unknown route.
 */
const NotFound: React.FC = () => {
    const navigate = useNavigate();

    return (
        <div id='not-found'>
            <h1>404</h1>
            <p>This page does not exist.</p>
            <TeaButton onClick={() => navigate('/', { replace: true })}>Go to Home</TeaButton>
        </div>
    );
};

export default NotFound;
