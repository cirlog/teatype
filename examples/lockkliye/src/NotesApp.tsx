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

// Components
import ModeCursor from '@/components/ModeCursor';
import { NoteEditor } from '@/components/NoteEditor';
import { Sidebar } from '@/components/Sidebar';

// Hooks
import useNotesStore from '@/hooks/useNotesStore';
import useKeyboardShortcuts from '@/hooks/useKeyboardShortcuts';

const NotesApp: React.FC = () => {
    const store = useNotesStore();

    useKeyboardShortcuts({
        onEscape: () => store.setFormatMode(null),
        onFormatToggle: store.toggleFormatMode,
        onUndo: store.undo,
        onRedo: store.redo,
    });

    const handleWordFormatChange = (
        blockId: string,
        wordId: string,
        format: Parameters<typeof store.updateWordFormat>[3]
    ) => {
        if (store.activeNoteId) {
            store.updateWordFormat(store.activeNoteId, blockId, wordId, format);
        }
    };

    const handleWordsChange = (blockId: string, words: Parameters<typeof store.setBlockWords>[2]) => {
        if (store.activeNoteId) {
            store.setBlockWords(store.activeNoteId, blockId, words);
        }
    };

    const handleBlockStyleChange = (blockId: string, style: Parameters<typeof store.updateBlockStyle>[2]) => {
        if (store.activeNoteId) {
            store.updateBlockStyle(store.activeNoteId, blockId, style);
        }
    };

    const handleBlockDelete = (blockId: string) => {
        if (store.activeNoteId) {
            store.deleteBlock(store.activeNoteId, blockId);
        }
    };

    const handleBlockAdd = (afterBlockId?: string) => {
        if (store.activeNoteId) {
            store.addBlock(store.activeNoteId, afterBlockId);
        }
    };

    const handleTitleChange = (title: string) => {
        if (store.activeNoteId) {
            store.updateNote(store.activeNoteId, { title });
        }
    };

    return (
        <div
            className={`notes-app ${store.sidebarExpanded ? '' : 'notes-app--fullscreen'} ${
                store.lightMode ? 'light-mode' : ''
            }`}
        >
            <Sidebar
                notes={store.notes}
                activeNoteId={store.activeNoteId}
                expanded={store.sidebarExpanded}
                lightMode={store.lightMode}
                editorWidth={store.editorWidth}
                onToggle={store.toggleSidebar}
                onNoteSelect={store.setActiveNote}
                onCreateNote={() => store.createNewNote()}
                onDeleteNote={store.deleteNote}
                onClearAllData={store.clearAllData}
                onToggleLightMode={store.toggleLightMode}
                onEditorWidthChange={store.setEditorWidth}
                onExportText={store.exportAsText}
                onExportJson={store.exportAsJson}
                onImportJson={store.importFromJson}
            />

            <main className='notes-app__main'>
                {store.activeNote ? (
                    <NoteEditor
                        note={store.activeNote}
                        formatMode={store.formatMode}
                        selectedColor={store.selectedColor}
                        selectedSize={store.selectedSize}
                        editorWidth={store.editorWidth}
                        historyCount={store.historyCount}
                        redoCount={store.redoCount}
                        canUndo={store.canUndo}
                        canRedo={store.canRedo}
                        onTitleChange={handleTitleChange}
                        onWordFormatChange={handleWordFormatChange}
                        onWordsChange={handleWordsChange}
                        onBlockStyleChange={handleBlockStyleChange}
                        onBlockDelete={handleBlockDelete}
                        onBlockAdd={handleBlockAdd}
                        onFormatModeChange={store.setFormatMode}
                        onColorChange={store.setSelectedColor}
                        onSizeChange={store.setSelectedSize}
                        onUndo={store.undo}
                        onRedo={store.redo}
                        getHistory={store.getActiveNoteHistory}
                    />
                ) : (
                    <div className='notes-app__empty'>
                        <div className='notes-app__empty-icon'>📝</div>
                        <h2>No note selected</h2>
                        <p>Select a note from the sidebar or create a new one</p>
                        <button onClick={() => store.createNewNote()}>Create New Note</button>
                    </div>
                )}
            </main>

            <ModeCursor formatMode={store.formatMode} selectedColor={store.selectedColor} />
        </div>
    );
};

export default NotesApp;
