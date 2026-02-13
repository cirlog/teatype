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

const enum AssetType {
    Animation = 'anim',
    Icon = 'icon',
    Image = 'img',
}

const enum FileExtension {
    SVG = '.svg',
    PNG = '.png',
}

type PathSegments = readonly string[];

const SEGMENT_DELIMITER = '/';
const PATH_PREFIX = '/';
const QUERY_PATTERN = /\?.*$/;
const BACKSLASH_PATTERN = /\\\\/g;

/** Default root path for assets */
const DEFAULT_ROOT = '';

/** Configurable root path - can be set once via path.setRoot() */
let assetRoot: string = DEFAULT_ROOT;

const normalizeRoot = (root: string): string => {
    // Remove trailing slash if present
    return root.endsWith('/') ? root.slice(0, -1) : root;
};

const joinSegments = (segments: PathSegments): string =>
    PATH_PREFIX + segments.join(SEGMENT_DELIMITER);

const buildAssetPath = (type: AssetType, ext: FileExtension) =>
    (...segments: string[]): string =>
        `${assetRoot}${joinSegments([type, ...segments])}${ext}`;

const stripOrigin = (url: string): string => {
    try {
        return url
            .replace(globalThis.location?.origin ?? '', '')
            .replace(QUERY_PATTERN, '')
            .replace(BACKSLASH_PATTERN, '');
    } catch {
        return url;
    }
};

const extractPathSegments = (url: string, startIdx: number, endOffset: number): string => {
    const sanitized = stripOrigin(url);
    const parts = sanitized.split(SEGMENT_DELIMITER);

    return parts.slice(startIdx, endOffset === 0 ? undefined : -endOffset).join(SEGMENT_DELIMITER);
};

/**
 * Asset path resolution utilities.
 * Provides type-safe path construction for icons, animations, and images.
 * 
 * @example
 * // Set root once at app initialization
 * path.setRoot('/teatype/media');
 * 
 * // Then use relative paths
 * path.icon('arrow');        // => '/teatype/media/icon/arrow.svg'
 * path.img('logo');          // => '/teatype/media/img/logo.png'
 * path.anim('spinner');      // => '/teatype/media/anim/spinner.svg'
 */
export const path = {
    /** 
     * Sets the root path for all asset utilities.
     * Call this once at app initialization.
     * @param root - The root path (e.g., '/teatype/media')
     */
    setRoot: (root: string): void => {
        assetRoot = normalizeRoot(root);
    },

    /** Gets the current root path */
    getRoot: (): string => assetRoot,

    /** Resets root to default (empty string) */
    resetRoot: (): void => {
        assetRoot = DEFAULT_ROOT;
    },

    /** Constructs animation asset path (.svg) */
    anim: buildAssetPath(AssetType.Animation, FileExtension.SVG),

    /** Constructs icon asset path (.svg) */
    icon: buildAssetPath(AssetType.Icon, FileExtension.SVG),

    /** Constructs image asset path (.png) */
    img: buildAssetPath(AssetType.Image, FileExtension.PNG),

    /** Joins path segments with leading slash */
    join: joinSegments,

    /** Extracts absolute path (removes first 2 and last segment) */
    absolute: (metaUrl: string): string => extractPathSegments(metaUrl, 2, 1),

    /** Returns sanitized component path */
    component: stripOrigin,
} as const;