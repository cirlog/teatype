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

const DatabaseIcon = () => {
    return (
        <svg fill='none' stroke='currentColor' viewBox='2.5 1.5 19 21'>
            <ellipse cx='12' cy='5' rx='9' ry='3' />
            <path d='M21 12c0 1.66-4 3-9 3s-9-1.34-9-3' />
            <path d='M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5' />
        </svg>
    );
};

export default DatabaseIcon;

export { DatabaseIcon };
