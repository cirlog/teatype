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

import React from 'react';

import type { iPhotoData } from '@/types';

interface iIPhonePreviewProps {
    photo: iPhotoData | null;
    applyFilter: boolean;
    showOverlay: boolean;
}

const IPhonePreview: React.FC<iIPhonePreviewProps> = ({ photo, applyFilter, showOverlay }) => {
    return (
        <div className='iphone-preview'>
            <div className='iphone-preview__frame'>
                {/* Dynamic Island */}
                {showOverlay && <div className='iphone-preview__dynamic-island' />}

                {/* Screen content */}
                <div className='iphone-preview__screen'>
                    {photo ? (
                        <>
                            {/* Blurred background */}
                            <div
                                className='iphone-preview__background'
                                style={{ backgroundImage: `url(${photo.src})` }}
                            />

                            {/* Polaroid */}
                            <div className='iphone-preview__polaroid'>
                                <div
                                    className='iphone-preview__polaroid-texture'
                                    style={{ backgroundImage: `url(${photo.src})` }}
                                />
                                <div className='iphone-preview__polaroid-photo-container'>
                                    <div
                                        className={`iphone-preview__polaroid-photo ${
                                            applyFilter ? 'iphone-preview__polaroid-photo--filtered' : ''
                                        }`}
                                        style={{ backgroundImage: `url(${photo.src})` }}
                                    />
                                    {applyFilter && (
                                        <>
                                            <div className='iphone-preview__polaroid-gloss' />
                                            <div className='iphone-preview__polaroid-grain' />
                                        </>
                                    )}
                                </div>
                                <div className='iphone-preview__polaroid-label'>
                                    <span className='iphone-preview__polaroid-title'>
                                        {photo.metadata.title || 'Untitled'}
                                    </span>
                                    <span className='iphone-preview__polaroid-meta'>
                                        {[photo.metadata.date, photo.metadata.location].filter(Boolean).join(' • ')}
                                    </span>
                                </div>
                            </div>

                            {/* iPhone Overlay Elements */}
                            {showOverlay && (
                                <>
                                    {/* Status bar */}
                                    <div className='iphone-preview__status-bar'>
                                        <span className='iphone-preview__carrier'>WLAN</span>
                                        <div className='iphone-preview__status-icons'>
                                            <span>📶</span>
                                            <span>📡</span>
                                            <span className='iphone-preview__battery'>🔋 84</span>
                                        </div>
                                    </div>

                                    {/* Date */}
                                    <div className='iphone-preview__date'>So. 11. KW2</div>

                                    {/* Clock */}
                                    <div className='iphone-preview__clock'>10:58</div>

                                    {/* Bottom buttons */}
                                    <div className='iphone-preview__bottom-bar'>
                                        <div className='iphone-preview__bottom-button'>🔦</div>
                                        <div className='iphone-preview__focus-mode'>🌙 Nicht stören</div>
                                        <div className='iphone-preview__bottom-button'>📷</div>
                                    </div>
                                </>
                            )}
                        </>
                    ) : (
                        <div className='iphone-preview__empty'>
                            <span>Upload a photo to preview</span>
                        </div>
                    )}
                </div>

                {/* Home indicator */}
                {showOverlay && <div className='iphone-preview__home-indicator' />}
            </div>
        </div>
    );
};

export default IPhonePreview;
