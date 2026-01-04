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
import { createNote, createFolder, createBlock, createWord, FORMAT_COLORS, exportNotesAsText, exportNotesAsJson, importNotesFromJson } from '@/types';

const STORAGE_KEY = 'lockkliye-data';
const HISTORY_KEY = 'lockkliye-history';
const REDO_KEY = 'lockkliye-redo';
const MAX_HISTORY_SIZE = 100;

const getInitialState = (): iNotesState => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
        try {
            const parsed = JSON.parse(stored);
            // Ensure lightMode, selectedSize, and editorWidth exist
            return {
                ...parsed,
                lightMode: parsed.lightMode ?? false,
                selectedSize: parsed.selectedSize ?? 'normal',
                editorWidth: parsed.editorWidth ?? 70,
            };
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
        selectedSize: 'normal',
        lightMode: false,
        editorWidth: 70,
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

const getInitialRedo = (): iHistoryEntry[] => {
    const stored = localStorage.getItem(REDO_KEY);
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
    const [redoStack, setRedoStack] = useState<iHistoryEntry[]>(getInitialRedo);
    const isUndoing = useRef(false);

    // Persist to localStorage
    useEffect(() => {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    }, [state]);

    // Persist history to localStorage
    useEffect(() => {
        localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    }, [history]);

    // Persist redo to localStorage
    useEffect(() => {
        localStorage.setItem(REDO_KEY, JSON.stringify(redoStack));
    }, [redoStack]);

    // Save state to history before modifications (per-note)
    const saveToHistory = useCallback((noteId: string, description: string) => {
        if (isUndoing.current) return;

        const note = state.notes.find((n: iNote) => n.id === noteId);
        if (!note) return;

        setHistory((prev: iHistoryEntry[]) => {
            const newEntry: iHistoryEntry = {
                noteId,
                note: JSON.parse(JSON.stringify(note)), // Deep clone
                timestamp: Date.now(),
                description,
            };
            const newHistory = [...prev, newEntry];
            // Limit history size
            if (newHistory.length > MAX_HISTORY_SIZE) {
                return newHistory.slice(-MAX_HISTORY_SIZE);
            }
            return newHistory;
        });

        // Clear redo stack on new change
        setRedoStack([]);
    }, [state.notes]);

    // Get history for active note
    const getActiveNoteHistory = useCallback(() => {
        if (!state.activeNoteId) return [];
        return history.filter((h: iHistoryEntry) => h.noteId === state.activeNoteId);
    }, [history, state.activeNoteId]);

    // Undo - restore previous state for active note
    const undo = useCallback(() => {
        const noteHistory = getActiveNoteHistory();
        if (noteHistory.length === 0) return;

        isUndoing.current = true;
        const previousEntry = noteHistory[noteHistory.length - 1];

        // Save current state to redo stack
        const currentNote = state.notes.find((n: iNote) => n.id === state.activeNoteId);
        if (currentNote) {
            setRedoStack((prev: iHistoryEntry[]) => [...prev, {
                noteId: currentNote.id,
                note: JSON.parse(JSON.stringify(currentNote)),
                timestamp: Date.now(),
                description: 'Redo',
            }]);
        }

        setState((prev: iNotesState) => ({
            ...prev,
            notes: prev.notes.map((n: iNote) =>
                n.id === previousEntry.noteId ? previousEntry.note : n
            ),
        }));

        setHistory((prev: iHistoryEntry[]) => prev.filter((h: iHistoryEntry) => h !== previousEntry));

        setTimeout(() => {
            isUndoing.current = false;
        }, 0);
    }, [getActiveNoteHistory, state.notes, state.activeNoteId]);

    // Redo - restore from redo stack
    const redo = useCallback(() => {
        const noteRedos = redoStack.filter((r: iHistoryEntry) => r.noteId === state.activeNoteId);
        if (noteRedos.length === 0) return;

        isUndoing.current = true;
        const redoEntry = noteRedos[noteRedos.length - 1];

        // Save current state to history
        const currentNote = state.notes.find((n: iNote) => n.id === state.activeNoteId);
        if (currentNote) {
            setHistory((prev: iHistoryEntry[]) => [...prev, {
                noteId: currentNote.id,
                note: JSON.parse(JSON.stringify(currentNote)),
                timestamp: Date.now(),
                description: 'Before redo',
            }]);
        }

        setState((prev: iNotesState) => ({
            ...prev,
            notes: prev.notes.map((n: iNote) =>
                n.id === redoEntry.noteId ? redoEntry.note : n
            ),
        }));

        setRedoStack((prev: iHistoryEntry[]) => prev.filter((r: iHistoryEntry) => r !== redoEntry));

        setTimeout(() => {
            isUndoing.current = false;
        }, 0);
    }, [redoStack, state.notes, state.activeNoteId]);

    // Check if undo/redo is available
    const canUndo = getActiveNoteHistory().length > 0;
    const canRedo = redoStack.filter((r: iHistoryEntry) => r.noteId === state.activeNoteId).length > 0;
    const historyCount = getActiveNoteHistory().length;
    const redoCount = redoStack.filter((r: iHistoryEntry) => r.noteId === state.activeNoteId).length;

    const activeNote = state.notes.find((n: iNote) => n.id === state.activeNoteId) || null;

    // Note actions
    const createNewNote = useCallback((folderId?: string) => {
        const note = createNote('Untitled', folderId || state.activeFolderId);
        setState((prev: iNotesState) => ({
            ...prev,
            notes: [note, ...prev.notes],
            activeNoteId: note.id,
        }));
        return note;
    }, [state.activeFolderId]);

    const updateNote = useCallback((noteId: string, updates: Partial<iNote>) => {
        saveToHistory(noteId, 'Update note');
        setState((prev: iNotesState) => ({
            ...prev,
            notes: prev.notes.map((n: iNote) =>
                n.id === noteId
                    ? { ...n, ...updates, updatedAt: Date.now() }
                    : n
            ),
        }));
    }, [saveToHistory]);

    const deleteNote = useCallback((noteId: string) => {
        setState((prev: iNotesState) => {
            const newNotes = prev.notes.filter((n: iNote) => n.id !== noteId);
            return {
                ...prev,
                notes: newNotes,
                activeNoteId: prev.activeNoteId === noteId
                    ? (newNotes[0]?.id || null)
                    : prev.activeNoteId,
            };
        });
        // Clear history for deleted note
        setHistory((prev: iHistoryEntry[]) => prev.filter((h: iHistoryEntry) => h.noteId !== noteId));
        setRedoStack((prev: iHistoryEntry[]) => prev.filter((r: iHistoryEntry) => r.noteId !== noteId));
    }, []);

    const setActiveNote = useCallback((noteId: string | null) => {
        setState((prev: iNotesState) => ({ ...prev, activeNoteId: noteId }));
    }, []);

    // Folder actions
    const createNewFolder = useCallback((name: string) => {
        const folder = createFolder(name);
        setState((prev: iNotesState) => ({
            ...prev,
            folders: [...prev.folders, folder],
        }));
        return folder;
    }, []);

    const updateFolder = useCallback((folderId: string, updates: Partial<iFolder>) => {
        setState((prev: iNotesState) => ({
            ...prev,
            folders: prev.folders.map((f: iFolder) =>
                f.id === folderId ? { ...f, ...updates } : f
            ),
        }));
    }, []);

    const deleteFolder = useCallback((folderId: string) => {
        setState((prev: iNotesState) => ({
            ...prev,
            folders: prev.folders.filter((f: iFolder) => f.id !== folderId),
            notes: prev.notes.map((n: iNote) =>
                n.folderId === folderId ? { ...n, folderId: null } : n
            ),
        }));
    }, []);

    const setActiveFolder = useCallback((folderId: string | null) => {
        setState((prev: iNotesState) => ({ ...prev, activeFolderId: folderId }));
    }, []);

    // Sidebar
    const toggleSidebar = useCallback(() => {
        setState((prev: iNotesState) => ({ ...prev, sidebarExpanded: !prev.sidebarExpanded }));
    }, []);

    const setSidebarExpanded = useCallback((expanded: boolean) => {
        setState((prev: iNotesState) => ({ ...prev, sidebarExpanded: expanded }));
    }, []);

    // Format mode
    const setFormatMode = useCallback((mode: tFormatMode) => {
        setState((prev: iNotesState) => ({ ...prev, formatMode: mode }));
    }, []);

    const toggleFormatMode = useCallback((mode: tFormatMode) => {
        setState((prev: iNotesState) => ({
            ...prev,
            formatMode: prev.formatMode === mode ? null : mode,
        }));
    }, []);

    const setSelectedColor = useCallback((color: string) => {
        setState((prev: iNotesState) => ({ ...prev, selectedColor: color }));
    }, []);

    const setSelectedSize = useCallback((size: string) => {
        setState((prev: iNotesState) => ({ ...prev, selectedSize: size }));
    }, []);

    // Light mode toggle
    const setLightMode = useCallback((lightMode: boolean) => {
        setState((prev: iNotesState) => ({ ...prev, lightMode }));
    }, []);

    const toggleLightMode = useCallback(() => {
        setState((prev: iNotesState) => ({ ...prev, lightMode: !prev.lightMode }));
    }, []);

    // Editor width setting
    const setEditorWidth = useCallback((width: number) => {
        setState((prev: iNotesState) => ({ ...prev, editorWidth: Math.max(50, Math.min(100, width)) }));
    }, []);

    // Word formatting
    const updateWordFormat = useCallback((
        noteId: string,
        blockId: string,
        wordId: string,
        formatUpdates: Partial<iWord['format']>
    ) => {
        saveToHistory(noteId, 'Format word');
        setState((prev: iNotesState) => ({
            ...prev,
            notes: prev.notes.map((note: iNote) => {
                if (note.id !== noteId) return note;
                return {
                    ...note,
                    updatedAt: Date.now(),
                    blocks: note.blocks.map((block: iTextBlock) => {
                        if (block.id !== blockId) return block;
                        return {
                            ...block,
                            words: block.words.map((word: iWord) => {
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
    }, [saveToHistory]);

    // Block operations
    const addBlock = useCallback((noteId: string, afterBlockId?: string, style?: iBlockStyle) => {
        saveToHistory(noteId, 'Add block');
        const newBlock = createBlock([createWord('')], style);
        setState((prev: iNotesState) => ({
            ...prev,
            notes: prev.notes.map((note: iNote) => {
                if (note.id !== noteId) return note;
                if (!afterBlockId) {
                    return { ...note, blocks: [...note.blocks, newBlock], updatedAt: Date.now() };
                }
                const idx = note.blocks.findIndex((b: iTextBlock) => b.id === afterBlockId);
                const newBlocks = [...note.blocks];
                newBlocks.splice(idx + 1, 0, newBlock);
                return { ...note, blocks: newBlocks, updatedAt: Date.now() };
            }),
        }));
        return newBlock;
    }, [saveToHistory]);

    const updateBlock = useCallback((noteId: string, blockId: string, updates: Partial<iTextBlock>) => {
        saveToHistory(noteId, 'Update block');
        setState((prev: iNotesState) => ({
            ...prev,
            notes: prev.notes.map((note: iNote) => {
                if (note.id !== noteId) return note;
                return {
                    ...note,
                    updatedAt: Date.now(),
                    blocks: note.blocks.map((block: iTextBlock) =>
                        block.id === blockId ? { ...block, ...updates } : block
                    ),
                };
            }),
        }));
    }, [saveToHistory]);

    const updateBlockStyle = useCallback((noteId: string, blockId: string, style: Partial<iBlockStyle>) => {
        saveToHistory(noteId, 'Update block style');
        setState((prev: iNotesState) => ({
            ...prev,
            notes: prev.notes.map((note: iNote) => {
                if (note.id !== noteId) return note;
                return {
                    ...note,
                    updatedAt: Date.now(),
                    blocks: note.blocks.map((block: iTextBlock) =>
                        block.id === blockId
                            ? { ...block, style: { ...block.style, ...style } }
                            : block
                    ),
                };
            }),
        }));
    }, [saveToHistory]);

    const deleteBlock = useCallback((noteId: string, blockId: string) => {
        saveToHistory(noteId, 'Delete block');
        setState((prev: iNotesState) => ({
            ...prev,
            notes: prev.notes.map((note: iNote) => {
                if (note.id !== noteId) return note;
                const newBlocks = note.blocks.filter((b: iTextBlock) => b.id !== blockId);
                // Keep at least one block
                if (newBlocks.length === 0) {
                    newBlocks.push(createBlock([createWord('')]));
                }
                return { ...note, blocks: newBlocks, updatedAt: Date.now() };
            }),
        }));
    }, [saveToHistory]);

    // Update words in a block (for typing)
    const setBlockWords = useCallback((noteId: string, blockId: string, words: iWord[]) => {
        saveToHistory(noteId, 'Edit text');
        setState((prev: iNotesState) => ({
            ...prev,
            notes: prev.notes.map((note: iNote) => {
                if (note.id !== noteId) return note;
                return {
                    ...note,
                    updatedAt: Date.now(),
                    blocks: note.blocks.map((block: iTextBlock) =>
                        block.id === blockId ? { ...block, words } : block
                    ),
                };
            }),
        }));
    }, [saveToHistory]);

    // Export functions
    const exportAsText = useCallback(() => {
        return exportNotesAsText(state.notes);
    }, [state.notes]);

    const exportAsJson = useCallback(() => {
        return exportNotesAsJson(state.notes, state.folders);
    }, [state.notes, state.folders]);

    const importFromJson = useCallback((jsonString: string) => {
        const result = importNotesFromJson(jsonString);
        if (result) {
            setState((prev: iNotesState) => ({
                ...prev,
                notes: [...result.notes, ...prev.notes],
                folders: [...result.folders.filter((f: iFolder) =>
                    !prev.folders.some((pf: iFolder) => pf.id === f.id)
                ), ...prev.folders],
            }));
            return true;
        }
        return false;
    }, []);

    // Clear all data
    const clearAllData = useCallback(() => {
        localStorage.removeItem(STORAGE_KEY);
        localStorage.removeItem(HISTORY_KEY);
        localStorage.removeItem(REDO_KEY);
        setHistory([]);
        setRedoStack([]);
        setState(getInitialState());
    }, []);

    return {
        // State
        ...state,
        activeNote,
        canUndo,
        canRedo,
        historyCount,
        redoCount,

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
        setSelectedSize,

        // Light mode
        setLightMode,
        toggleLightMode,

        // Editor width
        setEditorWidth,

        // Word/Block operations
        updateWordFormat,
        addBlock,
        updateBlock,
        updateBlockStyle,
        deleteBlock,
        setBlockWords,

        // History
        undo,
        redo,
        getActiveNoteHistory,

        // Export/Import
        exportAsText,
        exportAsJson,
        importFromJson,

        // Dev
        clearAllData,
    };
};

export default useNotesStore;

export type tNotesStore = ReturnType<typeof useNotesStore>;