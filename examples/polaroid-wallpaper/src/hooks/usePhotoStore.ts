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

import { useState, useCallback } from 'react';
import { v4 as uuid } from 'uuid';

import type { iPhotoData, iPhotoMetadata } from '@/types';
import { parseExifData, generateTitleFromFilename, readFileAsDataUrl, formatDate } from '@/util/imageUtils';

interface iUsePhotoStoreReturn {
    photos: iPhotoData[];
    activePhotoId: string | null;
    activePhoto: iPhotoData | null;
    addPhoto: (file: File) => Promise<void>;
    removePhoto: (id: string) => void;
    updatePhotoMetadata: (id: string, metadata: Partial<iPhotoMetadata>) => void;
    setActivePhoto: (id: string | null) => void;
    clearAll: () => void;
}

/**
 * Custom hook for managing photo state
 */
export function usePhotoStore(): iUsePhotoStoreReturn {
    const [photos, setPhotos] = useState<iPhotoData[]>([]);
    const [activePhotoId, setActivePhotoId] = useState<string | null>(null);

    const activePhoto = photos.find((p) => p.id === activePhotoId) || null;

    const addPhoto = useCallback(async (file: File) => {
        try {
            // Read file as data URL
            const src = await readFileAsDataUrl(file);

            // Parse EXIF data
            const exifData = await parseExifData(file);

            // Generate default metadata
            const metadata: iPhotoMetadata = {
                title: exifData.title || generateTitleFromFilename(file.name),
                date: exifData.date || formatDate(new Date()),
                location: exifData.location || '',
                filename: file.name,
            };

            const newPhoto: iPhotoData = {
                id: uuid(),
                src,
                metadata,
                file,
            };

            setPhotos((prev) => [...prev, newPhoto]);
            setActivePhotoId(newPhoto.id);
        } catch (error) {
            console.error('Failed to add photo:', error);
            throw error;
        }
    }, []);

    const removePhoto = useCallback(
        (id: string) => {
            setPhotos((prev) => prev.filter((p) => p.id !== id));
            if (activePhotoId === id) {
                setActivePhotoId(null);
            }
        },
        [activePhotoId]
    );

    const updatePhotoMetadata = useCallback((id: string, metadata: Partial<iPhotoMetadata>) => {
        setPhotos((prev) =>
            prev.map((photo) =>
                photo.id === id
                    ? {
                        ...photo,
                        metadata: { ...photo.metadata, ...metadata },
                    }
                    : photo
            )
        );
    }, []);

    const setActivePhoto = useCallback((id: string | null) => {
        setActivePhotoId(id);
    }, []);

    const clearAll = useCallback(() => {
        setPhotos([]);
        setActivePhotoId(null);
    }, []);

    return {
        photos,
        activePhotoId,
        activePhoto,
        addPhoto,
        removePhoto,
        updatePhotoMetadata,
        setActivePhoto,
        clearAll,
    };
}

export default usePhotoStore;
