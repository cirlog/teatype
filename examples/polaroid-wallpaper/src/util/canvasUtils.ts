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

import { IPHONE_16_PRO_MAX, type iPhotoData, type iExportSettings } from '@/types';

/**
 * Apply polaroid filter to an image
 * Creates a slightly faded, warm tone effect
 */
function applyPolaroidFilter(ctx: CanvasRenderingContext2D, width: number, height: number): void {
    const imageData = ctx.getImageData(0, 0, width, height);
    const data = imageData.data;

    for (let i = 0; i < data.length; i += 4) {
        // Slight warm tone shift
        data[i] = Math.min(255, data[i] * 1.05); // Red
        data[i + 1] = Math.min(255, data[i + 1] * 1.02); // Green
        data[i + 2] = Math.max(0, data[i + 2] * 0.95); // Blue (reduce slightly)

        // Reduce contrast slightly (move towards middle gray)
        const gray = (data[i] + data[i + 1] + data[i + 2]) / 3;
        const contrastFactor = 0.92;
        data[i] = gray + (data[i] - gray) * contrastFactor;
        data[i + 1] = gray + (data[i + 1] - gray) * contrastFactor;
        data[i + 2] = gray + (data[i + 2] - gray) * contrastFactor;

        // Slight fade effect (lift blacks)
        const fadeAmount = 15;
        data[i] = Math.min(255, data[i] + fadeAmount);
        data[i + 1] = Math.min(255, data[i + 1] + fadeAmount);
        data[i + 2] = Math.min(255, data[i + 2] + fadeAmount);
    }

    ctx.putImageData(imageData, 0, 0);
}

/**
 * Apply gloss overlay effect
 * Creates a shine/reflection effect like glossy photo paper
 */
function applyGlossOverlay(ctx: CanvasRenderingContext2D, width: number, height: number): void {
    // Create gradient for gloss effect
    const gradient = ctx.createLinearGradient(0, 0, width, height * 0.6);
    gradient.addColorStop(0, 'rgba(255, 255, 255, 0.35)');
    gradient.addColorStop(0.4, 'rgba(255, 255, 255, 0.1)');
    gradient.addColorStop(0.6, 'transparent');
    gradient.addColorStop(0.99, 'rgba(0, 0, 0, 0.25)');

    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);
}

/**
 * Apply grain/noise overlay effect
 * Creates a film grain texture for vintage look
 */
function applyGrainOverlay(ctx: CanvasRenderingContext2D, width: number, height: number): void {
    const imageData = ctx.getImageData(0, 0, width, height);
    const data = imageData.data;
    const grainIntensity = 12; // Lower = subtler grain

    for (let i = 0; i < data.length; i += 4) {
        const noise = (Math.random() - 0.5) * grainIntensity;
        data[i] = Math.min(255, Math.max(0, data[i] + noise)); // Red
        data[i + 1] = Math.min(255, Math.max(0, data[i + 1] + noise)); // Green
        data[i + 2] = Math.min(255, Math.max(0, data[i + 2] + noise)); // Blue
    }

    ctx.putImageData(imageData, 0, 0);
}

/**
 * Generate wallpaper canvas from photo data
 * @param photo - Photo data to generate wallpaper from
 * @param applyFilter - Whether to apply polaroid filter
 * @returns Promise resolving to canvas element
 */
export async function generateWallpaperCanvas(
    photo: iPhotoData,
    applyFilter: boolean = true
): Promise<HTMLCanvasElement> {
    const { width, height } = IPHONE_16_PRO_MAX;

    // Create main canvas
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d')!;

    // Load the image
    const img = await loadImage(photo.src);

    // Fill canvas with black first to prevent white edge bleeding from blur
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, width, height);

    // Draw blurred, darkened background (full screen)
    // Scale up slightly to prevent blur edge artifacts
    ctx.save();
    ctx.filter = 'blur(50px) brightness(0.4)';
    const blurMargin = 100; // Extra margin to prevent edge bleeding
    drawImageCover(ctx, img, -blurMargin, -blurMargin, width + blurMargin * 2, height + blurMargin * 2);
    ctx.filter = 'none';
    ctx.restore();

    // Calculate polaroid dimensions
    // No top padding - clock sits above the polaroid
    const polaroidWidth = width * 0.85;
    const polaroidPadding = width * 0.04;
    const polaroidTopPadding = polaroidPadding; // Same as side padding
    const polaroidBottomPadding = width * 0.12;

    // Photo area dimensions
    const photoWidth = polaroidWidth - polaroidPadding * 2;
    const photoHeight = photoWidth * (5 / 4); // 4:5 aspect ratio

    // Total polaroid height
    const polaroidHeight = polaroidTopPadding + photoHeight + polaroidBottomPadding;

    // Position polaroid - offset slightly towards top to leave room for bottom buttons
    const polaroidX = (width - polaroidWidth) / 2;
    const polaroidY = (height - polaroidHeight) / 2 - height * 0.03;

    // Draw polaroid shadow
    ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
    ctx.shadowBlur = 60;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 20;

    // Draw white polaroid frame
    ctx.fillStyle = '#fafafa';
    roundRect(ctx, polaroidX, polaroidY, polaroidWidth, polaroidHeight, 8);
    ctx.fill();

    // Reset shadow
    ctx.shadowColor = 'transparent';
    ctx.shadowBlur = 0;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 0;

    // Add subtle texture to polaroid using blurred image
    ctx.save();
    ctx.beginPath();
    roundRect(ctx, polaroidX, polaroidY, polaroidWidth, polaroidHeight, 8);
    ctx.clip();
    ctx.globalAlpha = 0.12;
    ctx.filter = 'blur(40px) brightness(1.5) saturate(0.3)';
    const textureMargin = 50;
    drawImageCover(ctx, img, polaroidX - textureMargin, polaroidY - textureMargin, polaroidWidth + textureMargin * 2, polaroidHeight + textureMargin * 2);
    ctx.restore();

    // Draw photo with filter
    const photoX = polaroidX + polaroidPadding;
    const photoY = polaroidY + polaroidTopPadding;

    // Create a temporary canvas for the photo with filter
    const photoCanvas = document.createElement('canvas');
    photoCanvas.width = photoWidth;
    photoCanvas.height = photoHeight;
    const photoCtx = photoCanvas.getContext('2d')!;

    // Draw image to fill photo area
    drawImageCover(photoCtx, img, 0, 0, photoWidth, photoHeight);

    // Apply polaroid filter if enabled (includes gloss and grain)
    if (applyFilter) {
        applyPolaroidFilter(photoCtx, photoWidth, photoHeight);
        applyGlossOverlay(photoCtx, photoWidth, photoHeight);
        applyGrainOverlay(photoCtx, photoWidth, photoHeight);
    }

    // Draw the photo onto main canvas
    ctx.drawImage(photoCanvas, photoX, photoY);

    // Draw label area
    const labelY = photoY + photoHeight + polaroidPadding;
    const labelCenterX = polaroidX + polaroidWidth / 2;

    // Title (handwritten style - we'll use a nice font in CSS, here we simulate)
    ctx.fillStyle = '#1a1a1a';
    ctx.font = `600 ${width * 0.038}px 'Caveat', cursive`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillText(photo.metadata.title || 'Untitled', labelCenterX, labelY);

    // Date and location
    ctx.font = `400 ${width * 0.022}px 'Inter', sans-serif`;
    ctx.fillStyle = '#666666';

    const dateLocationText = [photo.metadata.date, photo.metadata.location].filter(Boolean).join(' • ');

    if (dateLocationText) {
        ctx.fillText(dateLocationText, labelCenterX, labelY + width * 0.055);
    }

    return canvas;
}

/**
 * Export canvas as downloadable image
 * @param canvas - Canvas to export
 * @param filename - Filename for download
 * @param settings - Export settings
 */
export function exportCanvas(
    canvas: HTMLCanvasElement,
    filename: string,
    settings: iExportSettings = { quality: 1, format: 'png' }
): void {
    const mimeType = `image/${settings.format}`;
    const dataUrl = canvas.toDataURL(mimeType, settings.quality);

    const link = document.createElement('a');
    link.download = `${filename}.${settings.format}`;
    link.href = dataUrl;
    link.click();
}

/**
 * Load an image from URL
 */
function loadImage(src: string): Promise<HTMLImageElement> {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = () => resolve(img);
        img.onerror = () => reject(new Error('Failed to load image'));
        img.src = src;
    });
}

/**
 * Draw image to cover an area (like CSS object-fit: cover)
 */
function drawImageCover(
    ctx: CanvasRenderingContext2D,
    img: HTMLImageElement,
    x: number,
    y: number,
    width: number,
    height: number
): void {
    const imgRatio = img.width / img.height;
    const targetRatio = width / height;

    let sourceWidth = img.width;
    let sourceHeight = img.height;
    let sourceX = 0;
    let sourceY = 0;

    if (imgRatio > targetRatio) {
        // Image is wider than target
        sourceWidth = img.height * targetRatio;
        sourceX = (img.width - sourceWidth) / 2;
    } else {
        // Image is taller than target
        sourceHeight = img.width / targetRatio;
        sourceY = (img.height - sourceHeight) / 2;
    }

    ctx.drawImage(img, sourceX, sourceY, sourceWidth, sourceHeight, x, y, width, height);
}

/**
 * Draw a rounded rectangle
 */
function roundRect(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    width: number,
    height: number,
    radius: number
): void {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
}
