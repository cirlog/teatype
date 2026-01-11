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

interface iPhotoListProps {
    photos: iPhotoData[];
    activePhotoId: string | null;
    onSelect: (id: string) => void;
    onRemove: (id: string) => void;
}

const PhotoList: React.FC<iPhotoListProps> = ({ photos, activePhotoId, onSelect, onRemove }) => {
    if (photos.length === 0) {
        return null;
    }

    return (
        <div className='photo-list'>
            <h3>Your Photos ({photos.length})</h3>
            <div className='photo-list__grid'>
                {photos.map((photo) => (
                    <div
                        key={photo.id}
                        className={`photo-list__item ${photo.id === activePhotoId ? 'photo-list__item--active' : ''}`}
                        onClick={() => onSelect(photo.id)}
                    >
                        <div className='photo-list__thumbnail' style={{ backgroundImage: `url(${photo.src})` }} />
                        <div className='photo-list__info'>
                            <span className='photo-list__title'>{photo.metadata.title || 'Untitled'}</span>
                        </div>
                        <button
                            className='photo-list__remove'
                            onClick={(e) => {
                                e.stopPropagation();
                                onRemove(photo.id);
                            }}
                            title='Remove photo'
                        >
                            ×
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default PhotoList;
