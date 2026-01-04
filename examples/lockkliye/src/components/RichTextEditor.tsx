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
import { useRef, useCallback, useEffect, useState } from 'react';

// Components
import { applyFormatMode } from '@/components/WordComponent';

// Types
import { createWord, iWord, iWordFormat, tFormatMode } from '@/types';

interface iRichTextEditorProps {
    words: iWord[];
    formatMode: tFormatMode;
    selectedColor: string;
    selectedSize: string;
    onWordsChange: (words: iWord[]) => void;
    onAddBlockAfter: () => void;
    onClearFormatMode?: () => void;
    placeholder?: string;
}

// Generate inline styles from word format
const getWordStyle = (format: iWordFormat): React.CSSProperties => {
    const style: React.CSSProperties = {};

    if (format.bold) style.fontWeight = 'bold';
    if (format.italic) style.fontStyle = 'italic';
    if (format.underline) style.textDecoration = (style.textDecoration || '') + ' underline';
    if (format.strikethrough) style.textDecoration = (style.textDecoration || '') + ' line-through';
    // 'inherit' means use the default text color, so don't set any color style
    if (format.color && format.color !== 'inherit') style.color = format.color;
    if (format.highlight) style.backgroundColor = format.highlight;

    switch (format.fontSize) {
        case 'tiny':
            style.fontSize = '0.75em';
            break;
        case 'smaller':
            style.fontSize = '0.85em';
            break;
        case 'large':
            style.fontSize = '1.1em';
            break;
        case 'larger':
            style.fontSize = '1.25em';
            break;
        case 'huge':
            style.fontSize = '1.5em';
            break;
    }

    return style;
};

// Convert CSS style object to inline style string
const styleToString = (style: React.CSSProperties): string => {
    return Object.entries(style)
        .map(([key, value]) => {
            const cssKey = key.replace(/([A-Z])/g, '-$1').toLowerCase();
            return `${cssKey}: ${value}`;
        })
        .join('; ');
};

export const RichTextEditor: React.FC<iRichTextEditorProps> = ({
    words,
    formatMode,
    selectedColor,
    selectedSize: _selectedSize,
    onWordsChange,
    onAddBlockAfter,
    onClearFormatMode,
    placeholder = 'Click to edit...',
}) => {
    const editorRef = useRef<HTMLDivElement>(null);
    const [isFocused, setIsFocused] = useState(false);
    const wordsRef = useRef(words);

    // Keep wordsRef in sync
    useEffect(() => {
        wordsRef.current = words;
    }, [words]);

    // Update DOM to reflect words - call this after formatting
    const updateDOMContent = useCallback((wordList: iWord[]) => {
        if (!editorRef.current) return;
        const html = renderWordsAsHTML(wordList);
        if (html) {
            editorRef.current.innerHTML = html;
        }
    }, []);

    // Render words as HTML with formatting
    const renderWordsAsHTML = useCallback((wordList: iWord[]): string => {
        if (wordList.length === 0 || (wordList.length === 1 && !wordList[0].text)) {
            return '';
        }

        return wordList
            .map((word, idx) => {
                if (word.text === '\n') {
                    return '<br>';
                }

                const style = getWordStyle(word.format);
                const styleStr = styleToString(style);
                const space = idx < wordList.length - 1 && wordList[idx + 1]?.text !== '\n' ? ' ' : '';

                if (styleStr) {
                    return `<span data-word-id="${word.id}" style="${styleStr}">${word.text}</span>${space}`;
                }
                return `<span data-word-id="${word.id}">${word.text}</span>${space}`;
            })
            .join('');
    }, []);

    // Parse HTML content back to words
    const parseHTMLToWords = useCallback((element: HTMLElement): iWord[] => {
        const result: iWord[] = [];

        const processNode = (node: Node) => {
            if (node.nodeType === Node.TEXT_NODE) {
                const text = node.textContent || '';
                // Split by whitespace while preserving it
                const parts = text.split(/(\s+)/);

                parts.forEach((part) => {
                    if (part === '\n' || part.includes('\n')) {
                        // Handle newlines
                        const lines = part.split('\n');
                        lines.forEach((line, idx) => {
                            if (line.trim()) {
                                line.split(/\s+/)
                                    .filter(Boolean)
                                    .forEach((word) => {
                                        result.push(createWord(word));
                                    });
                            }
                            if (idx < lines.length - 1) {
                                result.push(createWord('\n'));
                            }
                        });
                    } else if (part.trim()) {
                        // Regular word - check if parent has style
                        const parent = node.parentElement;
                        let format: iWordFormat = {};

                        if (parent && parent.tagName === 'SPAN') {
                            const wordId = parent.getAttribute('data-word-id');
                            const existingWord = wordsRef.current.find((w) => w.id === wordId);

                            if (existingWord) {
                                format = { ...existingWord.format };
                            } else {
                                // Parse styles from the element
                                const style = parent.style;
                                if (style.fontWeight === 'bold') format.bold = true;
                                if (style.fontStyle === 'italic') format.italic = true;
                                if (style.textDecoration?.includes('underline')) format.underline = true;
                                if (style.textDecoration?.includes('line-through')) format.strikethrough = true;
                                if (style.color) format.color = style.color;
                                if (style.backgroundColor) format.highlight = style.backgroundColor;
                                if (style.fontSize) {
                                    const fs = style.fontSize;
                                    if (fs === '0.75em') format.fontSize = 'tiny';
                                    else if (fs === '0.85em') format.fontSize = 'smaller';
                                    else if (fs === '1.1em') format.fontSize = 'large';
                                    else if (fs === '1.25em') format.fontSize = 'larger';
                                    else if (fs === '1.5em') format.fontSize = 'huge';
                                }
                            }
                        }

                        result.push(createWord(part.trim(), format));
                    }
                });
            } else if (node.nodeType === Node.ELEMENT_NODE) {
                const el = node as HTMLElement;

                if (el.tagName === 'BR') {
                    result.push(createWord('\n'));
                    return;
                }

                if (el.tagName === 'DIV' && result.length > 0) {
                    // New div means new line (contenteditable behavior)
                    const lastWord = result[result.length - 1];
                    if (lastWord && lastWord.text !== '\n') {
                        result.push(createWord('\n'));
                    }
                }

                // Process children
                el.childNodes.forEach((child) => processNode(child));
            }
        };

        element.childNodes.forEach((child) => processNode(child));

        // Clean up: only remove truly empty results
        // Keep empty lines (newlines) as they are intentional
        if (result.length === 0) {
            return [createWord('')];
        }

        return result;
    }, []);

    // Save cursor position
    const saveCursorPosition = useCallback((): { start: number; end: number } | null => {
        const selection = window.getSelection();
        if (!selection || !selection.rangeCount || !editorRef.current) return null;

        const range = selection.getRangeAt(0);
        const preRange = range.cloneRange();
        preRange.selectNodeContents(editorRef.current);
        preRange.setEnd(range.startContainer, range.startOffset);
        const start = preRange.toString().length;

        const endRange = range.cloneRange();
        endRange.selectNodeContents(editorRef.current);
        endRange.setEnd(range.endContainer, range.endOffset);
        const end = endRange.toString().length;

        return { start, end };
    }, []);

    // Restore cursor position
    const restoreCursorPosition = useCallback((pos: { start: number; end: number }) => {
        if (!editorRef.current) return;

        const selection = window.getSelection();
        if (!selection) return;

        const range = document.createRange();
        let charCount = 0;
        let startNode: Node | null = null;
        let startOffset = 0;
        let endNode: Node | null = null;
        let endOffset = 0;

        const traverse = (node: Node): boolean => {
            if (node.nodeType === Node.TEXT_NODE) {
                const text = node.textContent || '';
                const textLen = text.length;

                if (!startNode && charCount + textLen >= pos.start) {
                    startNode = node;
                    startOffset = pos.start - charCount;
                }

                if (!endNode && charCount + textLen >= pos.end) {
                    endNode = node;
                    endOffset = pos.end - charCount;
                    return true; // Done
                }

                charCount += textLen;
            } else if (node.nodeType === Node.ELEMENT_NODE) {
                if ((node as HTMLElement).tagName === 'BR') {
                    charCount += 1;
                    if (!startNode && charCount >= pos.start) {
                        startNode = node;
                        startOffset = 0;
                    }
                    if (!endNode && charCount >= pos.end) {
                        endNode = node;
                        endOffset = 0;
                    }
                } else {
                    for (const child of Array.from(node.childNodes)) {
                        if (traverse(child)) return true;
                    }
                }
            }
            return false;
        };

        traverse(editorRef.current);

        if (startNode && endNode) {
            try {
                range.setStart(startNode, startOffset);
                range.setEnd(endNode, endOffset);
                selection.removeAllRanges();
                selection.addRange(range);
            } catch {
                // Cursor position failed, that's okay
            }
        }
    }, []);

    // Get currently selected word IDs
    const getSelectedWordIds = useCallback((): string[] => {
        const selection = window.getSelection();
        if (!selection || !selection.rangeCount || !editorRef.current) return [];

        const selectedIds: string[] = [];

        // Find all spans within the selection
        const spans = editorRef.current.querySelectorAll('span[data-word-id]');
        spans.forEach((span) => {
            if (selection.containsNode(span, true)) {
                const id = span.getAttribute('data-word-id');
                if (id) selectedIds.push(id);
            }
        });

        return selectedIds;
    }, []);

    // Apply formatting to selected words
    const applyFormattingToSelection = useCallback(() => {
        if (!formatMode || !editorRef.current) return false;

        const selectedIds = getSelectedWordIds();
        if (selectedIds.length === 0) return false;

        const savedCursor = saveCursorPosition();

        const newWords = wordsRef.current.map((word) => {
            if (selectedIds.includes(word.id)) {
                const updates = applyFormatMode(word.format, formatMode, selectedColor);
                return { ...word, format: { ...word.format, ...updates } };
            }
            return word;
        });

        // Update words ref immediately for instant update
        wordsRef.current = newWords;

        // Update state
        onWordsChange(newWords);

        // Instantly update DOM to show changes
        updateDOMContent(newWords);

        // Restore cursor after DOM update
        requestAnimationFrame(() => {
            if (savedCursor) {
                restoreCursorPosition(savedCursor);
            }
            // Clear format mode after applying (one-shot behavior)
            if (onClearFormatMode) {
                onClearFormatMode();
            }
        });

        return true;
    }, [
        formatMode,
        selectedColor,
        getSelectedWordIds,
        saveCursorPosition,
        restoreCursorPosition,
        onWordsChange,
        updateDOMContent,
        onClearFormatMode,
    ]);

    // Apply formatting to a single word by ID
    const applyFormattingToWord = useCallback(
        (wordId: string) => {
            if (!formatMode) return;

            const savedCursor = saveCursorPosition();

            const newWords = wordsRef.current.map((word) => {
                if (word.id === wordId) {
                    const updates = applyFormatMode(word.format, formatMode, selectedColor);
                    return { ...word, format: { ...word.format, ...updates } };
                }
                return word;
            });

            // Update words ref immediately
            wordsRef.current = newWords;

            onWordsChange(newWords);

            // Instantly update DOM
            updateDOMContent(newWords);

            // Restore cursor and clear format mode
            requestAnimationFrame(() => {
                if (savedCursor) {
                    restoreCursorPosition(savedCursor);
                }
                // Clear format mode after applying (one-shot behavior)
                if (onClearFormatMode) {
                    onClearFormatMode();
                }
            });
        },
        [
            formatMode,
            selectedColor,
            onWordsChange,
            saveCursorPosition,
            restoreCursorPosition,
            updateDOMContent,
            onClearFormatMode,
        ]
    );

    // Track previous format mode to detect changes
    const prevFormatModeRef = useRef<tFormatMode>(null);

    // Handle format mode changes - apply to selection when format mode is activated
    useEffect(() => {
        // Only apply if format mode changed from null/different to a new mode
        if (formatMode && prevFormatModeRef.current !== formatMode) {
            // Small delay to let selection settle
            const timer = setTimeout(() => {
                applyFormattingToSelection();
            }, 10);
            prevFormatModeRef.current = formatMode;
            return () => clearTimeout(timer);
        }
        if (!formatMode) {
            prevFormatModeRef.current = null;
        }
    }, [formatMode, applyFormattingToSelection]);

    // Handle input changes
    const handleInput = useCallback(() => {
        if (!editorRef.current) return;

        const newWords = parseHTMLToWords(editorRef.current);
        onWordsChange(newWords);

        // Don't restore cursor here - let the content update naturally
    }, [parseHTMLToWords, onWordsChange]);

    // Handle keyboard shortcuts
    const handleKeyDown = useCallback(
        (e: React.KeyboardEvent) => {
            if (e.key === 'Enter' && e.shiftKey) {
                e.preventDefault();
                onAddBlockAfter();
            }
            // Regular Enter inserts newline (default contenteditable behavior)
        },
        [onAddBlockAfter]
    );

    // Handle paste - strip formatting and insert plain text
    const handlePaste = useCallback((e: React.ClipboardEvent) => {
        e.preventDefault();
        const text = e.clipboardData.getData('text/plain');
        document.execCommand('insertText', false, text);
    }, []);

    // Handle click on words when in format mode
    const handleClick = useCallback(
        (e: React.MouseEvent) => {
            if (!formatMode || !editorRef.current) return;

            const target = e.target as HTMLElement;
            const wordSpan = target.closest('span[data-word-id]');

            if (wordSpan) {
                const wordId = wordSpan.getAttribute('data-word-id');
                if (wordId) {
                    // Check if there's a selection - if not, apply to clicked word
                    const selection = window.getSelection();
                    const hasSelection = selection && selection.toString().trim().length > 0;

                    if (!hasSelection) {
                        applyFormattingToWord(wordId);
                    } else {
                        // Apply to selection
                        applyFormattingToSelection();
                    }
                }
            }
        },
        [formatMode, applyFormattingToWord, applyFormattingToSelection]
    );

    // Sync content when words change externally
    useEffect(() => {
        if (!editorRef.current || isFocused) return;

        const html = renderWordsAsHTML(words);
        if (editorRef.current.innerHTML !== html) {
            editorRef.current.innerHTML = html || `<span class="rich-text-editor__placeholder">${placeholder}</span>`;
        }
    }, [words, isFocused, renderWordsAsHTML, placeholder]);

    // Initial render
    useEffect(() => {
        if (editorRef.current) {
            const html = renderWordsAsHTML(words);
            editorRef.current.innerHTML = html || `<span class="rich-text-editor__placeholder">${placeholder}</span>`;
        }
    }, []);

    const handleFocus = () => {
        setIsFocused(true);
        if (editorRef.current) {
            // Remove placeholder if present
            const ph = editorRef.current.querySelector('.rich-text-editor__placeholder');
            if (ph) {
                editorRef.current.innerHTML = '';
            }
        }
    };

    const handleBlur = () => {
        setIsFocused(false);
        handleInput(); // Final save on blur

        // Show placeholder if empty
        if (editorRef.current && !editorRef.current.textContent?.trim()) {
            editorRef.current.innerHTML = `<span class="rich-text-editor__placeholder">${placeholder}</span>`;
        }
    };

    return (
        <div
            ref={editorRef}
            className={`rich-text-editor ${isFocused ? 'rich-text-editor--focused' : ''} ${
                formatMode ? 'rich-text-editor--format-mode' : ''
            }`}
            contentEditable
            suppressContentEditableWarning
            onInput={handleInput}
            onKeyDown={handleKeyDown}
            onPaste={handlePaste}
            onFocus={handleFocus}
            onBlur={handleBlur}
            onClick={handleClick}
            spellCheck={false}
        />
    );
};

export default RichTextEditor;
