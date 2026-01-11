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

import React, { useRef } from 'react';

interface iUploadZoneProps {
    onFileSelect: (file: File) => void;
    disabled?: boolean;
}

const UploadZone: React.FC<iUploadZoneProps> = ({ onFileSelect, disabled = false }) => {
    const inputRef = useRef<HTMLInputElement>(null);
    const [isDragging, setIsDragging] = React.useState(false);

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        if (!disabled) {
            setIsDragging(true);
        }
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);

        if (disabled) return;

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                onFileSelect(file);
            }
        }
    };

    const handleClick = () => {
        if (!disabled) {
            inputRef.current?.click();
        }
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (files && files.length > 0) {
            onFileSelect(files[0]);
        }
        // Reset input so same file can be selected again
        e.target.value = '';
    };

    return (
        <div
            className={`upload-zone ${isDragging ? 'upload-zone--dragging' : ''} ${
                disabled ? 'upload-zone--disabled' : ''
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={handleClick}
        >
            <input
                ref={inputRef}
                type='file'
                accept='image/*'
                onChange={handleFileChange}
                style={{ display: 'none' }}
            />
            <div className='upload-zone__content'>
                <div className='upload-zone__icon'>📷</div>
                <h3>Drop your travel photo here</h3>
                <p>or click to browse</p>
                <span className='upload-zone__hint'>Supports JPG, PNG, HEIC • EXIF data will be auto-parsed</span>
            </div>
        </div>
    );
};

export default UploadZone;
