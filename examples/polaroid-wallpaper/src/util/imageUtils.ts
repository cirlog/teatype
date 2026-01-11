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

import exifr from 'exifr';

import type { iPhotoMetadata } from '@/types';

/**
 * Parse EXIF data from an image file
 * @param file - The image file to parse
 * @returns Parsed photo metadata
 */
export async function parseExifData(file: File): Promise<Partial<iPhotoMetadata>> {
    try {
        const exif = await exifr.parse(file, {
            pick: ['DateTimeOriginal', 'CreateDate', 'GPSLatitude', 'GPSLongitude', 'ImageDescription'],
            gps: true,
        });

        if (!exif) {
            return {};
        }

        const metadata: Partial<iPhotoMetadata> = {};

        // Parse date
        const dateField = exif.DateTimeOriginal || exif.CreateDate;
        if (dateField) {
            const date = new Date(dateField);
            if (!isNaN(date.getTime())) {
                metadata.date = formatDate(date);
            }
        }

        // Parse GPS location if available
        if (exif.latitude && exif.longitude) {
            // For now, just store coordinates - could use reverse geocoding API
            metadata.location = `${exif.latitude.toFixed(4)}, ${exif.longitude.toFixed(4)}`;
        }

        // Parse description as title
        if (exif.ImageDescription) {
            metadata.title = exif.ImageDescription;
        }

        return metadata;
    } catch (error) {
        console.warn('Failed to parse EXIF data:', error);
        return {};
    }
}

/**
 * Format a date object to a readable string
 * @param date - Date object to format
 * @returns Formatted date string
 */
export function formatDate(date: Date): string {
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
    });
}

/**
 * Generate a title from filename
 * @param filename - The original filename
 * @returns A cleaned up title
 */
export function generateTitleFromFilename(filename: string): string {
    // Remove extension
    const withoutExt = filename.replace(/\.[^/.]+$/, '');
    // Replace underscores and dashes with spaces
    const withSpaces = withoutExt.replace(/[_-]/g, ' ');
    // Capitalize first letter of each word
    return withSpaces
        .split(' ')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(' ');
}

/**
 * Read a file as a data URL
 * @param file - File to read
 * @returns Promise resolving to data URL
 */
export function readFileAsDataUrl(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result as string);
        reader.onerror = () => reject(new Error('Failed to read file'));
        reader.readAsDataURL(file);
    });
}

/**
 * Load an image and get its dimensions
 * @param src - Image source URL
 * @returns Promise resolving to image element
 */
export function loadImage(src: string): Promise<HTMLImageElement> {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = () => reject(new Error('Failed to load image'));
        img.src = src;
    });
}
