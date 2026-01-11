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

import React, { useState, useCallback } from 'react';

import type { iPhotoData, iExportSettings } from '@/types';
import { generateWallpaperCanvas, exportCanvas } from '@/util/canvasUtils';

interface iExportControlsProps {
    photo: iPhotoData | null;
    applyFilter: boolean;
    onFilterToggle: () => void;
}

const ExportControls: React.FC<iExportControlsProps> = ({ photo, applyFilter, onFilterToggle }) => {
    const [isExporting, setIsExporting] = useState(false);
    const [exportSettings, setExportSettings] = useState<iExportSettings>({
        quality: 1,
        format: 'png',
    });

    const handleExport = useCallback(async () => {
        if (!photo) return;

        setIsExporting(true);
        try {
            const canvas = await generateWallpaperCanvas(photo, applyFilter);
            const filename = `polaroid-${photo.metadata.title.toLowerCase().replace(/\s+/g, '-')}-wallpaper`;
            exportCanvas(canvas, filename, exportSettings);
        } catch (error) {
            console.error('Failed to export:', error);
            alert('Failed to generate wallpaper. Please try again.');
        } finally {
            setIsExporting(false);
        }
    }, [photo, applyFilter, exportSettings]);

    return (
        <div className='export-controls'>
            <h3>Export Settings</h3>

            <div className='export-controls__option'>
                <label className='export-controls__checkbox'>
                    <input type='checkbox' checked={applyFilter} onChange={onFilterToggle} />
                    <span>Apply Polaroid Filter</span>
                </label>
                <p className='export-controls__hint'>Adds a warm, slightly faded vintage look</p>
            </div>

            <div className='export-controls__option'>
                <label htmlFor='format'>Format</label>
                <select
                    id='format'
                    value={exportSettings.format}
                    onChange={(e) =>
                        setExportSettings((s) => ({ ...s, format: e.target.value as 'png' | 'jpeg' | 'webp' }))
                    }
                >
                    <option value='png'>PNG (Best Quality)</option>
                    <option value='jpeg'>JPEG (Smaller Size)</option>
                    <option value='webp'>WebP (Modern)</option>
                </select>
            </div>

            {exportSettings.format !== 'png' && (
                <div className='export-controls__option'>
                    <label htmlFor='quality'>Quality: {Math.round(exportSettings.quality * 100)}%</label>
                    <input
                        id='quality'
                        type='range'
                        min='0.5'
                        max='1'
                        step='0.05'
                        value={exportSettings.quality}
                        onChange={(e) => setExportSettings((s) => ({ ...s, quality: parseFloat(e.target.value) }))}
                    />
                </div>
            )}

            <button className='export-controls__button' onClick={handleExport} disabled={!photo || isExporting}>
                {isExporting ? 'Generating...' : 'Download Wallpaper'}
            </button>

            <p className='export-controls__info'>Output: 1320 × 2868 pixels (iPhone 16 Pro Max)</p>
        </div>
    );
};

export default ExportControls;
