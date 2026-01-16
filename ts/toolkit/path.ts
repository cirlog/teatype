/**
 * @license
 * Copyright (c) 2024-2025 enamentis GmbH. All rights reserved.
 *
 * This software module is the proprietary property of enamentis GmbH.
 * Unauthorized copying, modification, distribution, or use of this software
 * is strictly prohibited unless explicitly authorized in writing.
 *
 * THIS SOFTWARE IS PROVIDED "AS IS," WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NONINFRINGEMENT.
 * IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
 * DAMAGES, OR OTHER LIABILITY ARISING FROM THE USE OF THIS SOFTWARE.
 *
 * For more details, check the LICENSE file in the root directory of this repository.
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

const joinSegments = (segments: PathSegments): string =>
    PATH_PREFIX + segments.join(SEGMENT_DELIMITER);

const buildAssetPath = (type: AssetType, ext: FileExtension) =>
    (...segments: string[]): string =>
        `${joinSegments([type, ...segments])}${ext}`;

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
 */
export const path = {
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