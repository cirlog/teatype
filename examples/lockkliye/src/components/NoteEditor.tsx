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

// React imports
import { useState } from 'react';

// Components
import FloatingToolbar from './FloatingToolbar';
import { TextBlockComponent } from './TextBlockComponent';

// Types
import type { iNote, iTextBlock, iWord, tFormatMode, iHistoryEntry } from '@/types';

interface iNoteEditorProps {
    note: iNote;
    formatMode: tFormatMode;
    selectedColor: string;
    selectedSize: string;
    historyCount: number;
    redoCount: number;
    canUndo: boolean;
    canRedo: boolean;
    onTitleChange: (title: string) => void;
    onWordFormatChange: (blockId: string, wordId: string, format: Partial<iWord['format']>) => void;
    onWordsChange: (blockId: string, words: iWord[]) => void;
    onBlockStyleChange: (blockId: string, style: Partial<iTextBlock['style']>) => void;
    onBlockDelete: (blockId: string) => void;
    onBlockAdd: (afterBlockId?: string) => void;
    onFormatModeChange: (mode: tFormatMode) => void;
    onColorChange: (color: string) => void;
    onSizeChange: (size: string) => void;
    onUndo: () => void;
    onRedo: () => void;
    getHistory: () => iHistoryEntry[];
}

export const NoteEditor = ({
    note,
    formatMode,
    selectedColor,
    selectedSize,
    historyCount,
    redoCount: _redoCount,
    canUndo,
    canRedo,
    onTitleChange,
    onWordFormatChange,
    onWordsChange,
    onBlockStyleChange,
    onBlockDelete,
    onBlockAdd,
    onFormatModeChange,
    onColorChange,
    onSizeChange,
    onUndo,
    onRedo,
    getHistory,
}: iNoteEditorProps) => {
    const [isEditingTitle, setIsEditingTitle] = useState(false);
    const [titleValue, setTitleValue] = useState(note.title);
    const [showHistory, setShowHistory] = useState(false);

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
            <div className='note-editor__toolbar-row'>
                <FloatingToolbar
                    formatMode={formatMode}
                    selectedColor={selectedColor}
                    selectedSize={selectedSize}
                    onFormatModeChange={onFormatModeChange}
                    onColorChange={onColorChange}
                    onSizeChange={onSizeChange}
                />
            </div>

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

            {/* History indicator - bottom center, sticky */}
            <div className='note-editor__history-bar'>
                <div className='note-editor__history-indicator'>
                    <button
                        className={`note-editor__undo-btn ${!canUndo ? 'note-editor__undo-btn--disabled' : ''}`}
                        onClick={onUndo}
                        disabled={!canUndo}
                        title='Undo (Ctrl+Z)'
                    >
                        ↩
                    </button>

                    <button
                        className={`note-editor__history-btn ${
                            historyCount === 0 ? 'note-editor__history-btn--disabled' : ''
                        }`}
                        onClick={() => historyCount > 0 && setShowHistory(!showHistory)}
                        disabled={historyCount === 0}
                        title={`${historyCount} change${historyCount !== 1 ? 's' : ''} - Click to view history`}
                    >
                        <span className='note-editor__history-count'>{historyCount}</span>
                        <span className='note-editor__history-label'>changes</span>
                    </button>

                    <button
                        className={`note-editor__redo-btn ${!canRedo ? 'note-editor__redo-btn--disabled' : ''}`}
                        onClick={onRedo}
                        disabled={!canRedo}
                        title='Redo (Ctrl+Shift+Z)'
                    >
                        ↪
                    </button>

                    {showHistory && historyCount > 0 && (
                        <div className='note-editor__history-dropdown note-editor__history-dropdown--above'>
                            <div className='note-editor__history-header'>
                                <span>History ({historyCount})</span>
                                <button onClick={() => setShowHistory(false)}>×</button>
                            </div>
                            <div className='note-editor__history-list'>
                                {getHistory()
                                    .slice()
                                    .reverse()
                                    .map((entry) => (
                                        <div key={entry.timestamp} className='note-editor__history-item'>
                                            <span className='note-editor__history-item-desc'>{entry.description}</span>
                                            <span className='note-editor__history-item-time'>
                                                {new Date(entry.timestamp).toLocaleTimeString([], {
                                                    hour: '2-digit',
                                                    minute: '2-digit',
                                                    second: '2-digit',
                                                })}
                                            </span>
                                        </div>
                                    ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
