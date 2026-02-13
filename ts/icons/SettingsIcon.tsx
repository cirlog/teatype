/**
 * @license
 * Copyright (c) 2024-2025 enamentis GmbH. All rights reserved.
 *
 * This software module is the proprietary property of enamentis GmbH.
 * Unauthorized copying, modification, distribution, or use of this software
 * is strictly prohibited unless explicitly authorized in writing.
 *
 * THIS SOFTWARE IS PROVIDED "AS IS," WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NONINFRINGEMENT.
 * IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
 * DAMAGES, OR OTHER LIABILITY ARISING FROM THE USE OF THIS SOFTWARE.
 *
 * For more details, check the LICENSE file in the root directory of this repository.
 */

const SettingsIcon = () => {
    return (
        <svg
            fill='none'
            stroke='currentColor'
            height='512'
            viewBox='0 0 32 32'
            width='512'
            xmlns='http://www.w3.org/2000/svg'
        >
            <g data-name='Layer 2'>
                <path d='M24.49 4.25a3 3 0 0 0-2.56-1.48H10.07a3 3 0 0 0-2.56 1.48L1.58 14.52a3 3 0 0 0 0 3l5.93 10.23a3 3 0 0 0 2.56 1.48h11.86a3 3 0 0 0 2.56-1.48l5.93-10.27a3 3 0 0 0 0-3zm4.2 12.23-5.93 10.27a1 1 0 0 1-.83.48H10.07a1 1 0 0 1-.83-.48L3.31 16.48a1 1 0 0 1 0-1L9.24 5.25a1 1 0 0 1 .83-.48h11.86a1 1 0 0 1 .83.48l5.93 10.27a1 1 0 0 1 0 .96' />
                <path d='M16 10a6 6 0 1 0 6 6 6 6 0 0 0-6-6m0 10a4 4 0 1 1 4-4 4 4 0 0 1-4 4' />
            </g>
        </svg>
    );
};

export default SettingsIcon;

export { SettingsIcon };
