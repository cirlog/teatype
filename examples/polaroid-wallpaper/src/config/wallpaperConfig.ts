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
 * Shared configuration for wallpaper styling
 * These values are used by BOTH the canvas export and the CSS preview
 * to ensure visual consistency between what you see and what you export.
 * 
 * All percentage values are relative to SCREEN WIDTH unless noted otherwise.
 */
export const WALLPAPER_CONFIG = {
    // ===========================================
    // POLAROID DIMENSIONS (% of screen width)
    // ===========================================

    /** Polaroid width as percentage of screen width */
    polaroidWidth: 0.85, // 85%

    /** Padding on sides and top of polaroid (% of screen width) */
    polaroidPadding: 0.04, // 4%

    /** Bottom padding for label area (% of screen width) */
    polaroidBottomPadding: 0.12, // 12%

    /** Vertical offset from center (negative = up) as % of screen height */
    polaroidVerticalOffset: -0.03, // 3% up from center

    // ===========================================
    // PHOTO SETTINGS
    // ===========================================

    /** Photo aspect ratio (width / height) - classic polaroid is 4:5 */
    photoAspectRatio: 4 / 5,

    // ===========================================
    // BACKGROUND BLUR
    // ===========================================

    /** Background blur amount in pixels (for canvas) */
    backgroundBlur: 15,

    /** Background brightness (0-1) */
    backgroundBrightness: 0.85,

    // ===========================================
    // POLAROID TEXTURE OVERLAY
    // ===========================================

    /** Texture blur amount in pixels */
    textureBlur: 40,

    /** Texture brightness multiplier */
    textureBrightness: 1.5,

    /** Texture saturation (0 = grayscale, 1 = normal) */
    textureSaturation: 0.3,

    /** Texture opacity (0-1) */
    textureOpacity: 0.12,

    // ===========================================
    // COLORS
    // ===========================================

    /** Polaroid frame background color */
    polaroidBackground: '#fafafa',

    /** Title text color */
    titleColor: '#1a1a1a',

    /** Meta text color (date, location) */
    metaColor: '#666666',

    // ===========================================
    // TYPOGRAPHY (% of screen width for canvas)
    // ===========================================

    /** Title font size as % of screen width */
    titleFontSize: 0.038, // 3.8%

    /** Title font weight */
    titleFontWeight: 600,

    /** Title font family */
    titleFontFamily: "'Caveat', cursive",

    /** Meta font size as % of screen width */
    metaFontSize: 0.022, // 2.2%

    /** Meta font weight */
    metaFontWeight: 400,

    /** Meta font family */
    metaFontFamily: "'Inter', sans-serif",

    /** Gap between title and meta as % of screen width */
    titleMetaGap: 0.055, // 5.5%

    // ===========================================
    // SHADOW
    // ===========================================

    /** Shadow blur radius in pixels */
    shadowBlur: 60,

    /** Shadow Y offset in pixels */
    shadowOffsetY: 20,

    /** Shadow color */
    shadowColor: 'rgba(0, 0, 0, 0.5)',

    // ===========================================
    // BORDER RADIUS
    // ===========================================

    /** Polaroid border radius in pixels */
    polaroidBorderRadius: 8,
} as const;

/**
 * Calculate derived values for CSS
 * These convert screen-relative percentages to polaroid-relative percentages
 * (because CSS padding % is based on element width, not parent width)
 */
export function getCSSVariables(config: typeof WALLPAPER_CONFIG = WALLPAPER_CONFIG) {
    const polaroidWidthRatio = config.polaroidWidth;

    // Convert screen-relative % to polaroid-relative %
    const paddingAsPolaroidPercent = (config.polaroidPadding / polaroidWidthRatio) * 100;
    const bottomPaddingAsPolaroidPercent = (config.polaroidBottomPadding / polaroidWidthRatio) * 100;

    // Calculate polaroid center position
    // polaroidY = (height - polaroidHeight) / 2 - height * offset
    // As percentage: 50% - offset% (but we need to account for transform)
    const polaroidTopPercent = 50 + (config.polaroidVerticalOffset * 100);

    // Font sizes relative to polaroid width (for CSS)
    // In canvas: fontSize = screenWidth * ratio
    // In CSS: fontSize = polaroidWidth * (ratio / polaroidWidthRatio)
    // But polaroid is 85% of screen, so: fontSize = screenWidth * 0.85 * adjustedRatio
    // We want same visual size, so in CSS with polaroid as reference:
    // adjustedRatio = ratio / 0.85 (but then polaroid is % of screen...)
    // Actually simpler: use vw units in CSS based on screen width

    return {
        // Polaroid positioning and size
        '--polaroid-width': `${config.polaroidWidth * 100}%`,
        '--polaroid-top': `${polaroidTopPercent}%`,
        '--polaroid-padding': `${paddingAsPolaroidPercent}%`,
        '--polaroid-bottom-padding': `${bottomPaddingAsPolaroidPercent}%`,
        '--polaroid-border-radius': `${config.polaroidBorderRadius}px`,

        // Background
        '--bg-blur': `${config.backgroundBlur}px`,
        '--bg-brightness': `${config.backgroundBrightness}`,

        // Texture
        '--texture-blur': `${config.textureBlur}px`,
        '--texture-brightness': `${config.textureBrightness}`,
        '--texture-saturation': `${config.textureSaturation}`,
        '--texture-opacity': `${config.textureOpacity}`,

        // Colors
        '--polaroid-bg': config.polaroidBackground,
        '--title-color': config.titleColor,
        '--meta-color': config.metaColor,
        '--shadow-color': config.shadowColor,

        // Typography - using the polaroid-relative calculation
        // Preview screen width ≈ 306px, so we scale fonts proportionally
        // Canvas at 1320px: title = 1320 * 0.038 = 50.16px
        // Preview at 306px: title = 306 * 0.038 = 11.6px (too small!)
        // We need to use a ratio that works for the preview
        // Since preview screen is inside the polaroid parent, use em or calculate
        '--title-font-size': `${config.titleFontSize * 100}vw`,
        '--title-font-weight': `${config.titleFontWeight}`,
        '--title-font-family': config.titleFontFamily,
        '--meta-font-size': `${config.metaFontSize * 100}vw`,
        '--meta-font-weight': `${config.metaFontWeight}`,
        '--meta-font-family': config.metaFontFamily,
        '--title-meta-gap': `${config.titleMetaGap * 100}vw`,

        // Shadow
        '--shadow-blur': `${config.shadowBlur}px`,
        '--shadow-offset-y': `${config.shadowOffsetY}px`,
    } as const;
}

export type CSSVariables = ReturnType<typeof getCSSVariables>;