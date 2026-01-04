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

import { useState } from 'react';
import type { iNote, iTextBlock, iWord, tFormatMode } from '@/types';
import { TextBlockComponent } from './TextBlockComponent';
import { FloatingToolbar } from './FloatingToolbar';

interface iNoteEditorProps {
    note: iNote;
    formatMode: tFormatMode;
    selectedColor: string;
    onTitleChange: (title: string) => void;
    onWordFormatChange: (blockId: string, wordId: string, format: Partial<iWord['format']>) => void;
    onWordsChange: (blockId: string, words: iWord[]) => void;
    onBlockStyleChange: (blockId: string, style: Partial<iTextBlock['style']>) => void;
    onBlockDelete: (blockId: string) => void;
    onBlockAdd: (afterBlockId?: string) => void;
    onFormatModeChange: (mode: tFormatMode) => void;
    onColorChange: (color: string) => void;
}

export const NoteEditor = ({
    note,
    formatMode,
    selectedColor,
    onTitleChange,
    onWordFormatChange,
    onWordsChange,
    onBlockStyleChange,
    onBlockDelete,
    onBlockAdd,
    onFormatModeChange,
    onColorChange,
}: iNoteEditorProps) => {
    const [isEditingTitle, setIsEditingTitle] = useState(false);
    const [titleValue, setTitleValue] = useState(note.title);

    const handleTitleSubmit = () => {
        onTitleChange(titleValue || 'Untitled');
        setIsEditingTitle(false);
    };

    const formatDate = (timestamp: number) => {
        return new Date(timestamp).toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    return (
        <div className='note-editor'>
            <FloatingToolbar
                formatMode={formatMode}
                selectedColor={selectedColor}
                onFormatModeChange={onFormatModeChange}
                onColorChange={onColorChange}
            />

            <div className='note-editor__header'>
                {isEditingTitle ? (
                    <input
                        className='note-editor__title-input'
                        value={titleValue}
                        onChange={(e) => setTitleValue(e.target.value)}
                        onBlur={handleTitleSubmit}
                        onKeyDown={(e) => e.key === 'Enter' && handleTitleSubmit()}
                        autoFocus
                    />
                ) : (
                    <h1
                        className='note-editor__title'
                        onClick={() => {
                            setTitleValue(note.title);
                            setIsEditingTitle(true);
                        }}
                    >
                        {note.title}
                    </h1>
                )}
                <p className='note-editor__date'>Last edited: {formatDate(note.updatedAt)}</p>
            </div>

            <div className='note-editor__content'>
                {note.blocks.map((block) => (
                    <TextBlockComponent
                        key={block.id}
                        block={block}
                        formatMode={formatMode}
                        selectedColor={selectedColor}
                        onWordFormatChange={onWordFormatChange}
                        onWordsChange={onWordsChange}
                        onStyleChange={onBlockStyleChange}
                        onDelete={onBlockDelete}
                        onAddBlockAfter={onBlockAdd}
                    />
                ))}

                <button className='note-editor__add-block' onClick={() => onBlockAdd()}>
                    + Add block
                </button>
            </div>
        </div>
    );
};
