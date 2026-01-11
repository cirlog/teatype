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

import type { iPhotoMetadata } from '@/types';

interface iMetadataEditorProps {
    metadata: iPhotoMetadata;
    onChange: (metadata: Partial<iPhotoMetadata>) => void;
}

const MetadataEditor: React.FC<iMetadataEditorProps> = ({ metadata, onChange }) => {
    return (
        <div className='metadata-editor'>
            <h3>Edit Labels</h3>

            <div className='metadata-editor__field'>
                <label htmlFor='title'>Title</label>
                <input
                    id='title'
                    type='text'
                    value={metadata.title}
                    onChange={(e) => onChange({ title: e.target.value })}
                    placeholder='Enter a title...'
                />
            </div>

            <div className='metadata-editor__field'>
                <label htmlFor='date'>Date</label>
                <input
                    id='date'
                    type='text'
                    value={metadata.date}
                    onChange={(e) => onChange({ date: e.target.value })}
                    placeholder='e.g., January 15, 2026'
                />
            </div>

            <div className='metadata-editor__field'>
                <label htmlFor='location'>Location</label>
                <input
                    id='location'
                    type='text'
                    value={metadata.location}
                    onChange={(e) => onChange({ location: e.target.value })}
                    placeholder='e.g., Paris, France'
                />
            </div>

            <p className='metadata-editor__hint'>
                Tip: If your photo has EXIF data, the date and GPS coordinates were auto-filled. You can edit them to
                make them more readable.
            </p>
        </div>
    );
};

export default MetadataEditor;
