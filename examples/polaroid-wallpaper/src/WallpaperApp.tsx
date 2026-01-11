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

import React, { useState } from 'react';

// Components
import { UploadZone, MetadataEditor, IPhonePreview, PhotoList, ExportControls } from '@/components';

// Hooks
import usePhotoStore from '@/hooks/usePhotoStore';

const WallpaperApp: React.FC = () => {
    const store = usePhotoStore();
    const [applyFilter, setApplyFilter] = useState(true);

    const handleFileSelect = async (file: File) => {
        try {
            await store.addPhoto(file);
        } catch (error) {
            console.error('Failed to add photo:', error);
            alert('Failed to load photo. Please try a different image.');
        }
    };

    return (
        <div className='wallpaper-app'>
            <header className='wallpaper-app__header'>
                <h1>Polaroid Wallpaper Generator</h1>
                <p>Create beautiful iPhone 16 Pro Max wallpapers from your travel photos</p>
            </header>

            <main className='wallpaper-app__main'>
                <div className='wallpaper-app__sidebar'>
                    <UploadZone onFileSelect={handleFileSelect} />

                    <PhotoList
                        photos={store.photos}
                        activePhotoId={store.activePhotoId}
                        onSelect={store.setActivePhoto}
                        onRemove={store.removePhoto}
                    />

                    {store.activePhoto && (
                        <MetadataEditor
                            metadata={store.activePhoto.metadata}
                            onChange={(metadata) => store.updatePhotoMetadata(store.activePhoto!.id, metadata)}
                        />
                    )}

                    <ExportControls
                        photo={store.activePhoto}
                        applyFilter={applyFilter}
                        onFilterToggle={() => setApplyFilter(!applyFilter)}
                    />
                </div>

                <div className='wallpaper-app__preview'>
                    <IPhonePreview photo={store.activePhoto} applyFilter={applyFilter} />
                </div>
            </main>

            <footer className='wallpaper-app__footer'>
                <p>© 2026 Burak Günaydin • Resolution: 1320 × 2868 pixels</p>
            </footer>
        </div>
    );
};

export default WallpaperApp;
