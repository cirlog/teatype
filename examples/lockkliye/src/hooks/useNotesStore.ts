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
import React, { useState, useCallback, useEffect, useRef } from 'react';

// Types
import { iNote, iFolder, tFormatMode, iNotesState, iWord, iTextBlock, iBlockStyle, iHistoryEntry } from '@/types';

// Util
import { createNote, createFolder, createBlock, createWord, FORMAT_COLORS } from '@/types';

const STORAGE_KEY = 'lockkliye-data';
const HISTORY_KEY = 'lockkliye-history';
const MAX_HISTORY_SIZE = 100;

const getInitialState = (): iNotesState => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
        try {
            return JSON.parse(stored);
        } catch {
            // Fall through to default state
        }
    }

    // Create default state with sample data
    const defaultFolder = createFolder('All Notes');
    const sampleNote = createNote('Welcome to Notes', defaultFolder.id);
    sampleNote.blocks = [
        createBlock([
            createWord('Welcome', { bold: true, fontSize: 'larger' }),
            createWord('to'),
            createWord('Lockkliye', { italic: true, color: '#74c0fc' }),
            createWord('Notes', { bold: true, color: '#74c0fc' }),
        ]),
        createBlock([
            createWord('Try'),
            createWord('these'),
            createWord('shortcuts:'),
        ]),
        createBlock([
            createWord('CTRL+B', { bold: true, highlight: 'rgba(255,212,59,0.3)' }),
            createWord('for'),
            createWord('bold', { bold: true }),
            createWord('mode'),
        ], {
            borderStyle: 'solid',
            borderColor: 'rgba(255,212,59,0.5)',
            borderRadius: 8,
            backgroundColor: 'rgba(255,212,59,0.1)',
        }),
        createBlock([
            createWord('CTRL+I', { bold: true, highlight: 'rgba(116,192,252,0.3)' }),
            createWord('for'),
            createWord('italic', { italic: true }),
            createWord('mode'),
        ], {
            borderStyle: 'solid',
            borderColor: 'rgba(116,192,252,0.5)',
            borderRadius: 8,
            backgroundColor: 'rgba(116,192,252,0.1)',
        }),
    ];

    return {
        notes: [sampleNote],
        folders: [defaultFolder],
        activeNoteId: sampleNote.id,
        activeFolderId: defaultFolder.id,
        sidebarExpanded: true,
        formatMode: null,
        selectedColor: FORMAT_COLORS[0],
    };
};

const getInitialHistory = (): iHistoryEntry[] => {
    const stored = localStorage.getItem(HISTORY_KEY);
    if (stored) {
        try {
            return JSON.parse(stored);
        } catch {
            return [];
        }
    }
    return [];
};

const useNotesStore: React.FC = () => {
    const [state, setState] = useState<iNotesState>(getInitialState);
    const [history, setHistory] = useState<iHistoryEntry[]>(getInitialHistory);
    const isUndoing = useRef(false);

    // Persist to localStorage
    useEffect(() => {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    }, [state]);

    // Persist history to localStorage
    useEffect(() => {
        localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    }, [history]);

    // Save state to history before modifications
    const saveToHistory = useCallback((notes: iNote[]) => {
        if (isUndoing.current) return;

        setHistory(prev => {
            const newEntry: iHistoryEntry = {
                notes: JSON.parse(JSON.stringify(notes)), // Deep clone
                timestamp: Date.now(),
            };
            const newHistory = [...prev, newEntry];
            // Limit history size
            if (newHistory.length > MAX_HISTORY_SIZE) {
                return newHistory.slice(-MAX_HISTORY_SIZE);
            }
            return newHistory;
        });
    }, []);

    // Undo - restore previous state
    const undo = useCallback(() => {
        if (history.length === 0) return;

        isUndoing.current = true;
        const previousState = history[history.length - 1];

        setState(prev => ({
            ...prev,
            notes: previousState.notes,
        }));

        setHistory(prev => prev.slice(0, -1));

        // Reset flag after state update
        setTimeout(() => {
            isUndoing.current = false;
        }, 0);
    }, [history]);

    // Check if undo is available
    const canUndo = history.length > 0;

    const activeNote = state.notes.find(n => n.id === state.activeNoteId) || null;

    // Note actions
    const createNewNote = useCallback((folderId?: string) => {
        saveToHistory(state.notes);
        const note = createNote('Untitled', folderId || state.activeFolderId);
        setState(prev => ({
            ...prev,
            notes: [note, ...prev.notes],
            activeNoteId: note.id,
        }));
        return note;
    }, [state.activeFolderId, state.notes, saveToHistory]);

    const updateNote = useCallback((noteId: string, updates: Partial<iNote>) => {
        saveToHistory(state.notes);
        setState(prev => ({
            ...prev,
            notes: prev.notes.map(n =>
                n.id === noteId
                    ? { ...n, ...updates, updatedAt: Date.now() }
                    : n
            ),
        }));
    }, [state.notes, saveToHistory]);

    const deleteNote = useCallback((noteId: string) => {
        saveToHistory(state.notes);
        setState(prev => {
            const newNotes = prev.notes.filter(n => n.id !== noteId);
            return {
                ...prev,
                notes: newNotes,
                activeNoteId: prev.activeNoteId === noteId
                    ? (newNotes[0]?.id || null)
                    : prev.activeNoteId,
            };
        });
    }, [state.notes, saveToHistory]);

    const setActiveNote = useCallback((noteId: string | null) => {
        setState(prev => ({ ...prev, activeNoteId: noteId }));
    }, []);

    // Folder actions
    const createNewFolder = useCallback((name: string) => {
        const folder = createFolder(name);
        setState(prev => ({
            ...prev,
            folders: [...prev.folders, folder],
        }));
        return folder;
    }, []);

    const updateFolder = useCallback((folderId: string, updates: Partial<iFolder>) => {
        setState(prev => ({
            ...prev,
            folders: prev.folders.map(f =>
                f.id === folderId ? { ...f, ...updates } : f
            ),
        }));
    }, []);

    const deleteFolder = useCallback((folderId: string) => {
        setState(prev => ({
            ...prev,
            folders: prev.folders.filter(f => f.id !== folderId),
            notes: prev.notes.map(n =>
                n.folderId === folderId ? { ...n, folderId: null } : n
            ),
        }));
    }, []);

    const setActiveFolder = useCallback((folderId: string | null) => {
        setState(prev => ({ ...prev, activeFolderId: folderId }));
    }, []);

    // Sidebar
    const toggleSidebar = useCallback(() => {
        setState(prev => ({ ...prev, sidebarExpanded: !prev.sidebarExpanded }));
    }, []);

    const setSidebarExpanded = useCallback((expanded: boolean) => {
        setState(prev => ({ ...prev, sidebarExpanded: expanded }));
    }, []);

    // Format mode
    const setFormatMode = useCallback((mode: tFormatMode) => {
        setState(prev => ({ ...prev, formatMode: mode }));
    }, []);

    const toggleFormatMode = useCallback((mode: tFormatMode) => {
        setState(prev => ({
            ...prev,
            formatMode: prev.formatMode === mode ? null : mode,
        }));
    }, []);

    const setSelectedColor = useCallback((color: string) => {
        setState(prev => ({ ...prev, selectedColor: color }));
    }, []);

    // Word formatting
    const updateWordFormat = useCallback((
        noteId: string,
        blockId: string,
        wordId: string,
        formatUpdates: Partial<iWord['format']>
    ) => {
        saveToHistory(state.notes);
        setState(prev => ({
            ...prev,
            notes: prev.notes.map(note => {
                if (note.id !== noteId) return note;
                return {
                    ...note,
                    updatedAt: Date.now(),
                    blocks: note.blocks.map(block => {
                        if (block.id !== blockId) return block;
                        return {
                            ...block,
                            words: block.words.map(word => {
                                if (word.id !== wordId) return word;
                                return {
                                    ...word,
                                    format: { ...word.format, ...formatUpdates },
                                };
                            }),
                        };
                    }),
                };
            }),
        }));
    }, [state.notes, saveToHistory]);

    // Block operations
    const addBlock = useCallback((noteId: string, afterBlockId?: string, style?: iBlockStyle) => {
        saveToHistory(state.notes);
        const newBlock = createBlock([createWord('')], style);
        setState(prev => ({
            ...prev,
            notes: prev.notes.map(note => {
                if (note.id !== noteId) return note;
                if (!afterBlockId) {
                    return { ...note, blocks: [...note.blocks, newBlock], updatedAt: Date.now() };
                }
                const idx = note.blocks.findIndex(b => b.id === afterBlockId);
                const newBlocks = [...note.blocks];
                newBlocks.splice(idx + 1, 0, newBlock);
                return { ...note, blocks: newBlocks, updatedAt: Date.now() };
            }),
        }));
        return newBlock;
    }, [state.notes, saveToHistory]);

    const updateBlock = useCallback((noteId: string, blockId: string, updates: Partial<iTextBlock>) => {
        saveToHistory(state.notes);
        setState(prev => ({
            ...prev,
            notes: prev.notes.map(note => {
                if (note.id !== noteId) return note;
                return {
                    ...note,
                    updatedAt: Date.now(),
                    blocks: note.blocks.map(block =>
                        block.id === blockId ? { ...block, ...updates } : block
                    ),
                };
            }),
        }));
    }, [state.notes, saveToHistory]);

    const updateBlockStyle = useCallback((noteId: string, blockId: string, style: Partial<iBlockStyle>) => {
        saveToHistory(state.notes);
        setState(prev => ({
            ...prev,
            notes: prev.notes.map(note => {
                if (note.id !== noteId) return note;
                return {
                    ...note,
                    updatedAt: Date.now(),
                    blocks: note.blocks.map(block =>
                        block.id === blockId
                            ? { ...block, style: { ...block.style, ...style } }
                            : block
                    ),
                };
            }),
        }));
    }, [state.notes, saveToHistory]);

    const deleteBlock = useCallback((noteId: string, blockId: string) => {
        saveToHistory(state.notes);
        setState(prev => ({
            ...prev,
            notes: prev.notes.map(note => {
                if (note.id !== noteId) return note;
                const newBlocks = note.blocks.filter(b => b.id !== blockId);
                // Keep at least one block
                if (newBlocks.length === 0) {
                    newBlocks.push(createBlock([createWord('')]));
                }
                return { ...note, blocks: newBlocks, updatedAt: Date.now() };
            }),
        }));
    }, [state.notes, saveToHistory]);

    // Update words in a block (for typing)
    const setBlockWords = useCallback((noteId: string, blockId: string, words: iWord[]) => {
        saveToHistory(state.notes);
        setState(prev => ({
            ...prev,
            notes: prev.notes.map(note => {
                if (note.id !== noteId) return note;
                return {
                    ...note,
                    updatedAt: Date.now(),
                    blocks: note.blocks.map(block =>
                        block.id === blockId ? { ...block, words } : block
                    ),
                };
            }),
        }));
    }, [state.notes, saveToHistory]);

    // Clear all data
    const clearAllData = useCallback(() => {
        localStorage.removeItem(STORAGE_KEY);
        localStorage.removeItem(HISTORY_KEY);
        setHistory([]);
        setState(getInitialState());
    }, []);

    return {
        // State
        ...state,
        activeNote,
        canUndo,

        // Note actions
        createNewNote,
        updateNote,
        deleteNote,
        setActiveNote,

        // Folder actions
        createNewFolder,
        updateFolder,
        deleteFolder,
        setActiveFolder,

        // Sidebar
        toggleSidebar,
        setSidebarExpanded,

        // Format mode
        setFormatMode,
        toggleFormatMode,
        setSelectedColor,

        // Word/Block operations
        updateWordFormat,
        addBlock,
        updateBlock,
        updateBlockStyle,
        deleteBlock,
        setBlockWords,

        // History
        undo,

        // Dev
        clearAllData,
    };
};

export default useNotesStore;

export type tNotesStore = ReturnType<typeof useNotesStore>;