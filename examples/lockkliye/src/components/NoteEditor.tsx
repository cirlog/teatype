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
import { useState, useRef, useEffect, useMemo } from 'react';

// Components
import FloatingToolbar from './FloatingToolbar';
import { TextBlockComponent } from './TextBlockComponent';

// Types
import type { iNote, iTextBlock, iWord, tFormatMode, iHistoryEntry } from '@/types';

// Debounce utility for resize performance
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const debounce = <T extends (...args: any[]) => void>(fn: T, delay: number) => {
    let timeoutId: ReturnType<typeof setTimeout>;
    return (...args: Parameters<T>) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn(...args), delay);
    };
};

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
    const [editorWidth, setEditorWidth] = useState(800);
    const [isResizing, setIsResizing] = useState(false);
    const editorRef = useRef<HTMLDivElement>(null);

    // Debounced width update for smooth resizing
    const debouncedSetWidth = useMemo(() => debounce((width: number) => setEditorWidth(width), 16), []);

    // Handle editor resize
    useEffect(() => {
        if (!isResizing) return;

        const handleMouseMove = (e: MouseEvent) => {
            if (!editorRef.current) return;
            const editorRect = editorRef.current.getBoundingClientRect();
            const centerX = editorRect.left + editorRect.width / 2;
            // Calculate width based on distance from center (symmetric resize)
            const newWidth = Math.abs(e.clientX - centerX) * 2;
            const clampedWidth = Math.max(400, Math.min(1400, newWidth));
            debouncedSetWidth(clampedWidth);
        };

        const handleMouseUp = () => {
            setIsResizing(false);
        };

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);

        return () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        };
    }, [isResizing, debouncedSetWidth]);

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
        <div className={`note-editor ${isResizing ? 'note-editor--resizing' : ''}`}>
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

            <div ref={editorRef} className='note-editor__body' style={{ maxWidth: editorWidth }}>
                {/* Left resize handle */}
                <div
                    className='note-editor__resize-handle note-editor__resize-handle--left'
                    onMouseDown={() => setIsResizing(true)}
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
                            selectedSize={selectedSize}
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

                {/* Right resize handle */}
                <div
                    className='note-editor__resize-handle note-editor__resize-handle--right'
                    onMouseDown={() => setIsResizing(true)}
                />
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
