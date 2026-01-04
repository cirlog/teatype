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

import { useState, useRef, useCallback, useEffect } from 'react';
import type { iTextBlock, tFormatMode, iWord } from '@/types';
import { createWord } from '@/types';
import { WordComponent, applyFormatMode } from './WordComponent';

interface iTextBlockComponentProps {
    block: iTextBlock;
    formatMode: tFormatMode;
    selectedColor: string;
    onWordFormatChange: (blockId: string, wordId: string, format: Partial<iWord['format']>) => void;
    onWordsChange: (blockId: string, words: iWord[]) => void;
    onStyleChange: (blockId: string, style: Partial<iTextBlock['style']>) => void;
    onDelete: (blockId: string) => void;
    onAddBlockAfter: (blockId: string) => void;
}

// Helper to serialize words to editable text while preserving format info
interface iWordWithFormat {
    text: string;
    format: iWord['format'];
}

export const TextBlockComponent = ({
    block,
    formatMode,
    selectedColor,
    onWordFormatChange,
    onWordsChange,
    onStyleChange,
    onDelete,
    onAddBlockAfter,
}: iTextBlockComponentProps) => {
    const [hoveredWordId, setHoveredWordId] = useState<string | null>(null);
    const [isEditing, setIsEditing] = useState(false);
    const [editText, setEditText] = useState('');
    const [originalWords, setOriginalWords] = useState<iWordWithFormat[]>([]);
    const [showStyleMenu, setShowStyleMenu] = useState(false);
    const [isResizing, setIsResizing] = useState(false);
    const [isNearEdge, setIsNearEdge] = useState(false);
    const inputRef = useRef<HTMLTextAreaElement>(null);
    const styleMenuRef = useRef<HTMLDivElement>(null);
    const blockRef = useRef<HTMLDivElement>(null);

    const blockStyle = block.style;

    // Close style menu on outside click
    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            if (showStyleMenu && styleMenuRef.current && !styleMenuRef.current.contains(e.target as Node)) {
                setShowStyleMenu(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, [showStyleMenu]);

    // Handle width resizing
    useEffect(() => {
        if (!isResizing) return;

        const handleMouseMove = (e: MouseEvent) => {
            if (!blockRef.current) return;
            const container = blockRef.current.parentElement;
            if (!container) return;

            const containerRect = container.getBoundingClientRect();
            const blockRect = blockRef.current.getBoundingClientRect();

            // Calculate new width as percentage of container
            const newWidth = ((e.clientX - blockRect.left) / containerRect.width) * 100;
            const clampedWidth = Math.max(30, Math.min(100, newWidth));

            onStyleChange(block.id, { widthPercent: clampedWidth });
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
    }, [isResizing, block.id, onStyleChange]);

    // Detect when mouse is near right edge of block
    const handleMouseMoveOnBlock = (e: React.MouseEvent) => {
        if (!blockRef.current || isEditing) {
            setIsNearEdge(false);
            return;
        }
        const rect = blockRef.current.getBoundingClientRect();
        const nearEdgeThreshold = 15;
        const isNear = rect.right - e.clientX < nearEdgeThreshold;
        setIsNearEdge(isNear);
    };

    const handleMouseLeave = () => {
        if (!isResizing) {
            setIsNearEdge(false);
        }
    };

    const getBlockStyles = (): React.CSSProperties => {
        const styles: React.CSSProperties = {};

        if (blockStyle.widthPercent) {
            styles.width = `${blockStyle.widthPercent}%`;
        }

        if (blockStyle.borderStyle && blockStyle.borderStyle !== 'none') {
            styles.borderStyle = blockStyle.borderStyle;
            styles.borderWidth = '1px';
            styles.borderColor = blockStyle.borderColor || 'rgba(255,255,255,0.2)';
        }

        if (blockStyle.borderRadius) {
            styles.borderRadius = `${blockStyle.borderRadius}px`;
        }

        if (blockStyle.backgroundGradient) {
            styles.background = blockStyle.backgroundGradient;
        } else if (blockStyle.backgroundColor) {
            styles.backgroundColor = blockStyle.backgroundColor;
        }

        if (blockStyle.transparent) {
            styles.backgroundColor = 'transparent';
        }

        return styles;
    };

    const handleWordClick = (wordId: string) => {
        if (formatMode) {
            const word = block.words.find((w) => w.id === wordId);
            if (word) {
                const updates = applyFormatMode(word.format, formatMode, selectedColor);
                onWordFormatChange(block.id, wordId, updates);
            }
        }
    };

    const startEditing = () => {
        if (formatMode) return; // Don't edit in format mode
        // Join words with spaces, but convert newline words to actual newlines
        const text = block.words
            .map((w) => (w.text === '\n' ? '\n' : w.text))
            .join(' ')
            .replace(/ \n /g, '\n')
            .replace(/ \n/g, '\n')
            .replace(/\n /g, '\n');
        // Store original words with their formatting
        setOriginalWords(block.words.map((w) => ({ text: w.text, format: { ...w.format } })));
        setEditText(text);
        setIsEditing(true);
    };

    const finishEditing = useCallback(() => {
        // Split by whitespace but preserve newlines as separate "words"
        // First, normalize newlines and split
        const lines = editText.split('\n');
        const allWords: string[] = [];

        lines.forEach((line: string, lineIndex: number) => {
            const wordsInLine = line.split(/\s+/).filter(Boolean);
            allWords.push(...wordsInLine);
            // Add newline marker between lines (except for last line)
            if (lineIndex < lines.length - 1) {
                allWords.push('\n');
            }
        });

        if (allWords.length === 0 || (allWords.length === 1 && allWords[0] === '\n')) {
            onWordsChange(block.id, [createWord('')]);
            setIsEditing(false);
            return;
        }

        // Build a character-to-format map from original text
        // Each character position maps to its word's format
        const charFormatMap: Array<iWord['format'] | null> = [];
        let charIndex = 0;

        for (let i = 0; i < originalWords.length; i++) {
            const word = originalWords[i];
            for (let j = 0; j < word.text.length; j++) {
                charFormatMap[charIndex++] = word.format;
            }
            if (i < originalWords.length - 1) {
                charFormatMap[charIndex++] = null; // space has no format
            }
        }

        // Helper to find the best matching format for a new word
        const findBestFormat = (newWord: string, wordIndex: number): iWord['format'] | null => {
            // 1. Exact match at same position
            if (wordIndex < originalWords.length && originalWords[wordIndex].text === newWord) {
                return originalWords[wordIndex].format;
            }

            // 2. Exact match anywhere
            const exactMatch = originalWords.find((ow: iWordWithFormat) => ow.text === newWord);
            if (exactMatch) {
                return exactMatch.format;
            }

            // 3. Check if new word is a substring of any original word (word was split)
            for (const ow of originalWords) {
                if (ow.text.includes(newWord) || newWord.includes(ow.text)) {
                    return ow.format;
                }
            }

            // 4. Check if new word is similar to original at same position (letters added/removed)
            if (wordIndex < originalWords.length) {
                const orig = originalWords[wordIndex].text;
                // If they share a common prefix or suffix of at least 2 chars, consider it the same word
                const minLen = Math.min(orig.length, newWord.length);
                if (minLen >= 2) {
                    // Check common prefix
                    let prefixLen = 0;
                    for (let i = 0; i < minLen; i++) {
                        if (orig[i] === newWord[i]) prefixLen++;
                        else break;
                    }
                    // Check common suffix
                    let suffixLen = 0;
                    for (let i = 0; i < minLen; i++) {
                        if (orig[orig.length - 1 - i] === newWord[newWord.length - 1 - i]) suffixLen++;
                        else break;
                    }
                    // If significant overlap, preserve format
                    if (prefixLen >= 2 || suffixLen >= 2 || prefixLen + suffixLen >= minLen) {
                        return originalWords[wordIndex].format;
                    }
                }
            }

            // 5. If word count increased (split happened), check adjacent original words
            if (allWords.length > originalWords.length) {
                // Map new word index back to approximate original position
                const ratio = originalWords.length / allWords.length;
                const approxOrigIndex = Math.floor(wordIndex * ratio);
                if (approxOrigIndex < originalWords.length) {
                    return originalWords[approxOrigIndex].format;
                }
            }

            return null;
        };

        // Create new words with preserved formatting
        const newWords: iWord[] = allWords.map((text: string, index: number) => {
            if (text === '\n') {
                return createWord('\n'); // Newline word
            }
            const format = findBestFormat(text, index);
            return format ? createWord(text, format) : createWord(text);
        });

        onWordsChange(block.id, newWords);
        setIsEditing(false);
    }, [editText, block.id, onWordsChange, originalWords]);

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Escape') {
            finishEditing();
        } else if (e.key === 'Enter' && e.shiftKey) {
            // Shift+Enter: Add new block
            e.preventDefault();
            finishEditing();
            onAddBlockAfter(block.id);
        }
        // Regular Enter creates newline (default behavior, no need to prevent)
    };

    // Handle text changes, including bullet conversion
    const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        let newText = e.target.value;

        // Convert "- " at the start of a line to bullet point
        newText = newText.replace(/^- /gm, '• ');
        newText = newText.replace(/\n- /g, '\n• ');

        setEditText(newText);
    };

    // Auto-resize textarea to fit content
    const autoResizeTextarea = useCallback(() => {
        if (inputRef.current) {
            inputRef.current.style.height = 'auto';
            inputRef.current.style.height = `${inputRef.current.scrollHeight}px`;
        }
    }, []);

    useEffect(() => {
        if (isEditing && inputRef.current) {
            inputRef.current.focus();
            inputRef.current.selectionStart = inputRef.current.value.length;
            autoResizeTextarea();
        }
    }, [isEditing, autoResizeTextarea]);

    // Resize on text change
    useEffect(() => {
        autoResizeTextarea();
    }, [editText, autoResizeTextarea]);

    const borderStyles = ['none', 'solid', 'dashed', 'dotted', 'double'] as const;
    const bgColors = [
        'transparent',
        'rgba(255,107,107,0.1)',
        'rgba(255,169,77,0.1)',
        'rgba(255,212,59,0.1)',
        'rgba(105,219,124,0.1)',
        'rgba(116,192,252,0.1)',
        'rgba(177,151,252,0.1)',
    ];
    const gradients = [
        '',
        'linear-gradient(135deg, rgba(255,107,107,0.15) 0%, rgba(255,169,77,0.15) 100%)',
        'linear-gradient(135deg, rgba(116,192,252,0.15) 0%, rgba(177,151,252,0.15) 100%)',
        'linear-gradient(135deg, rgba(105,219,124,0.15) 0%, rgba(116,192,252,0.15) 100%)',
        'linear-gradient(135deg, rgba(247,131,172,0.15) 0%, rgba(177,151,252,0.15) 100%)',
    ];

    return (
        <div
            ref={blockRef}
            className={`text-block ${isEditing ? 'text-block--editing' : ''} ${
                isNearEdge || isResizing ? 'text-block--resizing' : ''
            }`}
            style={getBlockStyles()}
            onMouseMove={handleMouseMoveOnBlock}
            onMouseLeave={handleMouseLeave}
        >
            {/* Width resize handle */}
            {(isNearEdge || isResizing) && !isEditing && (
                <div
                    className='text-block__resize-handle'
                    onMouseDown={(e) => {
                        e.preventDefault();
                        setIsResizing(true);
                    }}
                />
            )}

            <div className='text-block__controls'>
                <button
                    className='text-block__style-btn'
                    onClick={() => setShowStyleMenu(!showStyleMenu)}
                    title='Block style'
                >
                    ◐
                </button>
                <button
                    className='text-block__add-btn'
                    onClick={() => onAddBlockAfter(block.id)}
                    title='Add block below'
                >
                    +
                </button>
                <button className='text-block__delete-btn' onClick={() => onDelete(block.id)} title='Delete block'>
                    ×
                </button>
            </div>

            {showStyleMenu && (
                <div className='text-block__style-menu' ref={styleMenuRef}>
                    <div className='style-menu__section'>
                        <span className='style-menu__label'>Border</span>
                        <div className='style-menu__options'>
                            {borderStyles.map((style) => (
                                <button
                                    key={style}
                                    className={`style-menu__option ${
                                        blockStyle.borderStyle === style ? 'style-menu__option--active' : ''
                                    }`}
                                    onClick={() => onStyleChange(block.id, { borderStyle: style })}
                                >
                                    {style}
                                </button>
                            ))}
                        </div>
                    </div>
                    <div className='style-menu__section'>
                        <span className='style-menu__label'>Background</span>
                        <div className='style-menu__colors'>
                            {bgColors.map((color, i) => (
                                <button
                                    key={i}
                                    className={`style-menu__color ${
                                        blockStyle.backgroundColor === color ? 'style-menu__color--active' : ''
                                    }`}
                                    style={{ backgroundColor: color || 'transparent' }}
                                    onClick={() =>
                                        onStyleChange(block.id, { backgroundColor: color, backgroundGradient: '' })
                                    }
                                />
                            ))}
                        </div>
                    </div>
                    <div className='style-menu__section'>
                        <span className='style-menu__label'>Gradient</span>
                        <div className='style-menu__colors'>
                            {gradients.map((grad, i) => (
                                <button
                                    key={i}
                                    className={`style-menu__color style-menu__color--gradient ${
                                        blockStyle.backgroundGradient === grad ? 'style-menu__color--active' : ''
                                    }`}
                                    style={{ background: grad || 'transparent' }}
                                    onClick={() =>
                                        onStyleChange(block.id, { backgroundGradient: grad, backgroundColor: '' })
                                    }
                                />
                            ))}
                        </div>
                    </div>
                    <div className='style-menu__section'>
                        <span className='style-menu__label'>Radius</span>
                        <input
                            type='range'
                            min='0'
                            max='24'
                            value={blockStyle.borderRadius || 0}
                            onChange={(e) => onStyleChange(block.id, { borderRadius: parseInt(e.target.value) })}
                        />
                    </div>
                </div>
            )}

            {isEditing ? (
                <textarea
                    ref={inputRef}
                    className='text-block__input'
                    value={editText}
                    onChange={handleTextChange}
                    onBlur={finishEditing}
                    onKeyDown={handleKeyDown}
                    placeholder='Type something...'
                    rows={1}
                />
            ) : (
                <div className='text-block__content' onClick={startEditing}>
                    {block.words.map((word, idx) => (
                        <span key={word.id}>
                            {word.text === '\n' ? (
                                <br />
                            ) : (
                                <>
                                    <WordComponent
                                        word={word}
                                        formatMode={formatMode}
                                        selectedColor={selectedColor}
                                        isHovered={hoveredWordId === word.id}
                                        onHover={setHoveredWordId}
                                        onClick={handleWordClick}
                                    />
                                    {idx < block.words.length - 1 && block.words[idx + 1]?.text !== '\n' && ' '}
                                </>
                            )}
                        </span>
                    ))}
                    {block.words.length === 0 || (block.words.length === 1 && !block.words[0].text) ? (
                        <span className='text-block__placeholder'>Click to edit...</span>
                    ) : null}
                </div>
            )}
        </div>
    );
};
