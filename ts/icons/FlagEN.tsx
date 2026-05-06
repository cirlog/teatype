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

const FlagEN = () => {
    return (
        <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 60 30'>
            <clipPath id='t'>
                <path d='M30,15 h30 v15 z v15 h-30 z h-30 v-15 z v-15 h30 z' />
            </clipPath>
            <path d='M0,0 v30 h60 v-30 z' fill='#012169' />
            <path d='M0,0 L60,30 M60,0 L0,30' stroke='#fff' stroke-width='6' />
            <path d='M0,0 L60,30 M60,0 L0,30' clip-path='url(#t)' stroke='#C8102E' stroke-width='4' />
            <path d='M30,0 v30 M0,15 h60' stroke='#fff' stroke-width='10' />
            <path d='M30,0 v30 M0,15 h60' stroke='#C8102E' stroke-width='6' />
        </svg>
    );
};

export default FlagEN;

export { FlagEN };
