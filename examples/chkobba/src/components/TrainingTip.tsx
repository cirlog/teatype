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
import React from 'react';

// Types
import { iTip } from '../engine/TrainingTips';

interface iTrainingTipProps {
    tip: iTip | null;
    enabled: boolean;
}

const TrainingTip: React.FC<iTrainingTipProps> = ({ tip, enabled }) => {
    if (!enabled || !tip) {
        return null;
    }

    const getCategoryClass = (category: string): string => {
        switch (category) {
            case 'opportunity':
                return 'training-tip--opportunity';
            case 'warning':
                return 'training-tip--warning';
            case 'info':
            default:
                return 'training-tip--info';
        }
    };

    return (
        <div className={`training-tip ${getCategoryClass(tip.category)}`}>
            <div className='training-tip-header'>
                <span className='training-tip-badge'>💡 TIP</span>
                <span className='training-tip-title'>{tip.title}</span>
            </div>
            <p className='training-tip-message'>{tip.message}</p>
        </div>
    );
};

export default TrainingTip;
