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

/**
 * Photo metadata interface
 */
export interface iPhotoMetadata {
    /** Photo title */
    title: string;
    /** Date taken */
    date: string;
    /** Location/place */
    location: string;
    /** Original filename */
    filename: string;
}

/**
 * Photo data interface for the wallpaper generator
 */
export interface iPhotoData {
    /** Unique identifier */
    id: string;
    /** Image source URL (data URL or blob URL) */
    src: string;
    /** Photo metadata */
    metadata: iPhotoMetadata;
    /** Original file for re-processing */
    file?: File;
}

/**
 * Wallpaper export settings
 */
export interface iExportSettings {
    /** Export quality (0-1) */
    quality: number;
    /** Export format */
    format: 'png' | 'jpeg' | 'webp';
}

/**
 * iPhone 16 Pro Max dimensions
 * Resolution: 1320 x 2868 pixels
 * Aspect ratio: ~19.5:9
 */
export const IPHONE_16_PRO_MAX = {
    width: 1320,
    height: 2868,
    aspectRatio: 1320 / 2868,
    // Safe areas for clock and home indicator
    statusBarHeight: 59, // Dynamic Island area
    homeIndicatorHeight: 34,
    // Notch/Dynamic Island dimensions
    dynamicIslandWidth: 162,
    dynamicIslandHeight: 52,
} as const;

/**
 * Polaroid styling constants
 */
export const POLAROID_STYLE = {
    // Border widths (as percentage of total width)
    borderSide: 0.04, // 4% on left and right
    borderTop: 0.06, // 6% on top (for clock area)
    borderBottom: 0.12, // 12% on bottom (for label area)
    // Photo area
    photoAspectRatio: 4 / 5, // Classic polaroid photo ratio
    // Shadow
    shadowBlur: 40,
    shadowSpread: 10,
    shadowOpacity: 0.4,
} as const;
