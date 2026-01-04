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

// Formatting modes that can be activated via shortcuts
type tFormatMode =
    | 'bold'
    | 'italic'
    | 'underline'
    | 'strikethrough'
    | 'color'
    | 'highlight'
    | 'larger'
    | 'smaller'
    | null;

// Word-level formatting attributes
interface iWordFormat {
    bold?: boolean;
    italic?: boolean;
    underline?: boolean;
    strikethrough?: boolean;
    color?: string;
    highlight?: string;
    fontSize?: 'smaller' | 'normal' | 'larger' | 'huge';
}

// Each word is its own component with formatting
interface iWord {
    id: string;
    text: string;
    format: iWordFormat;
}

// Block styles for text containers
interface iBlockStyle {
    borderStyle?: 'solid' | 'dashed' | 'dotted' | 'double' | 'none';
    borderColor?: string;
    borderRadius?: number;
    backgroundColor?: string;
    backgroundGradient?: string;
    transparent?: boolean;
}

// Text block containing words
interface iTextBlock {
    id: string;
    words: iWord[];
    style: iBlockStyle;
}

// Note document
interface iNote {
    id: string;
    title: string;
    blocks: iTextBlock[];
    folderId: string | null;
    createdAt: number;
    updatedAt: number;
    pinned?: boolean;
}

// Folder for organizing notes
interface iFolder {
    id: string;
    name: string;
    icon?: string;
    color?: string;
    expanded?: boolean;
}

// App state
interface iNotesState {
    notes: iNote[];
    folders: iFolder[];
    activeNoteId: string | null;
    activeFolderId: string | null;
    sidebarExpanded: boolean;
    formatMode: tFormatMode;
    selectedColor: string;
}

// History entry for undo functionality
interface iHistoryEntry {
    notes: iNote[];
    timestamp: number;
}

// Predefined colors for formatting
const FORMAT_COLORS = [
    '#ffffff', // white
    '#ff6b6b', // red
    '#ffa94d', // orange
    '#ffd43b', // yellow
    '#69db7c', // green
    '#74c0fc', // blue
    '#b197fc', // purple
    '#f783ac', // pink
];

// Predefined gradients for blocks
const BLOCK_GRADIENTS = [
    'linear-gradient(135deg, rgba(255,107,107,0.2) 0%, rgba(255,169,77,0.2) 100%)',
    'linear-gradient(135deg, rgba(116,192,252,0.2) 0%, rgba(177,151,252,0.2) 100%)',
    'linear-gradient(135deg, rgba(105,219,124,0.2) 0%, rgba(116,192,252,0.2) 100%)',
    'linear-gradient(135deg, rgba(247,131,172,0.2) 0%, rgba(177,151,252,0.2) 100%)',
    'linear-gradient(135deg, rgba(255,212,59,0.2) 0%, rgba(255,169,77,0.2) 100%)',
];

// Keyboard shortcuts mapping
const SHORTCUTS: Record<string, tFormatMode> = {
    'ctrl+b': 'bold',
    'ctrl+i': 'italic',
    'ctrl+u': 'underline',
    'ctrl+shift+s': 'strikethrough',
    'ctrl+shift+c': 'color',
    'ctrl+shift+h': 'highlight',
    'ctrl+]': 'larger',
    'ctrl+[': 'smaller',
};

// Helper to create a new word
const createWord = (text: string, format: iWordFormat = {}): iWord => ({
    id: crypto.randomUUID(),
    text,
    format,
});

// Helper to create a new block
const createBlock = (words: iWord[] = [], style: iBlockStyle = {}): iTextBlock => ({
    id: crypto.randomUUID(),
    words,
    style,
});

// Helper to create a new note
const createNote = (title: string = 'Untitled', folderId: string | null = null): iNote => ({
    id: crypto.randomUUID(),
    title,
    blocks: [createBlock([createWord('')])],
    folderId,
    createdAt: Date.now(),
    updatedAt: Date.now(),
});

// Helper to create a new folder
const createFolder = (name: string): iFolder => ({
    id: crypto.randomUUID(),
    name,
    expanded: true,
});

// Serialize note for storage/reconstruction
const serializeNote = (note: iNote): string => JSON.stringify(note);

// Deserialize note from storage
const deserializeNote = (data: string): iNote => JSON.parse(data);

export type {
    iBlockStyle,
    iFolder,
    iHistoryEntry,
    iNote,
    iNotesState,
    iTextBlock,
    iWord,
    iWordFormat,
    tFormatMode,
};

export {
    BLOCK_GRADIENTS,
    FORMAT_COLORS,
    SHORTCUTS,

    createBlock,
    createFolder,
    createNote,
    createWord,
    deserializeNote,
    serializeNote,
};