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
import type { iNote } from '@/types';

interface iSidebarProps {
    notes: iNote[];
    activeNoteId: string | null;
    expanded: boolean;
    onToggle: () => void;
    onNoteSelect: (noteId: string) => void;
    onCreateNote: () => void;
    onDeleteNote: (noteId: string) => void;
    onClearAllData: () => void;
}

export const Sidebar = ({
    notes,
    activeNoteId,
    expanded,
    onToggle,
    onNoteSelect,
    onCreateNote,
    onDeleteNote,
    onClearAllData,
}: iSidebarProps) => {
    const [showSettings, setShowSettings] = useState(false);
    const formatDate = (timestamp: number) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));

        if (days === 0) {
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } else if (days === 1) {
            return 'Yesterday';
        } else if (days < 7) {
            return date.toLocaleDateString([], { weekday: 'short' });
        } else {
            return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
        }
    };

    const getNotePreview = (note: iNote): string => {
        const words = note.blocks.flatMap((b) => b.words.map((w) => w.text)).filter(Boolean);
        return words.slice(0, 10).join(' ') || 'No content';
    };

    return (
        <aside className={`sidebar ${expanded ? 'sidebar--expanded' : 'sidebar--collapsed'}`}>
            <div className='sidebar__header'>
                <button className='sidebar__toggle' onClick={onToggle} title={expanded ? 'Collapse' : 'Expand'}>
                    <span className='sidebar__toggle-icon'>{expanded ? '◀' : '▶'}</span>
                </button>
                {expanded && (
                    <>
                        <h2 className='sidebar__title'>Notes</h2>
                        <button className='sidebar__new-note' onClick={onCreateNote} title='New Note'>
                            <span>+</span>
                        </button>
                    </>
                )}
            </div>

            {expanded && (
                <>
                    <div className='sidebar__notes'>
                        <div className='sidebar__section-header'>
                            <span>All Notes</span>
                            <span className='sidebar__count'>{notes.length}</span>
                        </div>

                        <div className='sidebar__notes-list'>
                            {notes.length === 0 ? (
                                <div className='sidebar__empty'>No notes yet. Click + to create one.</div>
                            ) : (
                                notes
                                    .sort((a, b) => b.updatedAt - a.updatedAt)
                                    .map((note) => (
                                        <button
                                            key={note.id}
                                            className={`sidebar__note ${
                                                activeNoteId === note.id ? 'sidebar__note--active' : ''
                                            }`}
                                            onClick={() => onNoteSelect(note.id)}
                                        >
                                            <div className='sidebar__note-header'>
                                                <span className='sidebar__note-title'>{note.title}</span>
                                                <button
                                                    className='sidebar__note-delete'
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        onDeleteNote(note.id);
                                                    }}
                                                    title='Delete note'
                                                >
                                                    ×
                                                </button>
                                            </div>
                                            <div className='sidebar__note-meta'>
                                                <span className='sidebar__note-date'>{formatDate(note.updatedAt)}</span>
                                                <span className='sidebar__note-preview'>{getNotePreview(note)}</span>
                                            </div>
                                        </button>
                                    ))
                            )}
                        </div>
                    </div>

                    <div className='sidebar__footer'>
                        <button className='sidebar__settings-btn' onClick={() => setShowSettings(!showSettings)}>
                            <span>⚙</span>
                            <span>Settings</span>
                        </button>

                        {showSettings && (
                            <div className='sidebar__settings'>
                                <div className='sidebar__settings-section'>
                                    <span className='sidebar__settings-label'>Developer</span>
                                    <button
                                        className='sidebar__clear-data-btn'
                                        onClick={() => {
                                            if (
                                                confirm(
                                                    'Are you sure you want to clear all data? This cannot be undone.'
                                                )
                                            ) {
                                                onClearAllData();
                                            }
                                        }}
                                    >
                                        Clear All Data
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </>
            )}
        </aside>
    );
};
