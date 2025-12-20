/**
 * Training tip display component
 */

import React from 'react';
import { Tip } from '../game/TrainingTips';

interface TrainingTipProps {
    tip: Tip | null;
    enabled: boolean;
}

const TrainingTip: React.FC<TrainingTipProps> = ({ tip, enabled }) => {
    if (!enabled || !tip) {
        return null;
    }

    const getCategoryClass = (category: string): string => {
        switch (category) {
            case 'opportunity':
                return 'training-tip--opportunity';
            case 'warning':
                return 'training-tip--warning';
            case 'strategy':
                return 'training-tip--strategy';
            case 'info':
            default:
                return 'training-tip--info';
        }
    };

    return (
        <div className={`training-tip ${getCategoryClass(tip.category)}`}>
            <div className='training-tip__header'>
                <span className='training-tip__badge'>💡 TIPP</span>
                <span className='training-tip__title'>{tip.title}</span>
            </div>
            <p className='training-tip__message'>{tip.message}</p>
        </div>
    );
};

export default TrainingTip;
