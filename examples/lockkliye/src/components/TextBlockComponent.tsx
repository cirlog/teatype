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

import { useState, useRef, useEffect } from 'react';
import type { iTextBlock, tFormatMode, iWord } from '@/types';
import { RichTextEditor } from './RichTextEditor';

interface iTextBlockComponentProps {
    block: iTextBlock;
    formatMode: tFormatMode;
    selectedColor: string;
    selectedSize: string;
    onWordFormatChange: (blockId: string, wordId: string, format: Partial<iWord['format']>) => void;
    onWordsChange: (blockId: string, words: iWord[]) => void;
    onStyleChange: (blockId: string, style: Partial<iTextBlock['style']>) => void;
    onDelete: (blockId: string) => void;
    onAddBlockAfter: (blockId: string) => void;
    onEditingChange?: (blockId: string, isEditing: boolean) => void;
    onClearFormatMode?: () => void;
}

export const TextBlockComponent = ({
    block,
    formatMode,
    selectedColor,
    selectedSize,
    onWordsChange,
    onStyleChange,
    onDelete,
    onAddBlockAfter,
    onClearFormatMode,
    confirmDeletions = true,
    customColors = [],
    customGradients = [],
    onAddCustomColor,
    onAddCustomGradient,
}: iTextBlockComponentProps & {
    confirmDeletions?: boolean;
    customColors?: string[];
    customGradients?: string[];
    onAddCustomColor?: (color: string) => void;
    onAddCustomGradient?: (gradient: string) => void;
}) => {
    const [showStyleMenu, setShowStyleMenu] = useState(false);
    const [isResizing, setIsResizing] = useState(false);
    const [isNearEdge, setIsNearEdge] = useState(false);
    const [titleInput, setTitleInput] = useState(block.style.title || '');
    const [showCustomColorPicker, setShowCustomColorPicker] = useState(false);
    const [showCustomGradientPicker, setShowCustomGradientPicker] = useState(false);
    const [customColorInput, setCustomColorInput] = useState('#ff0000');
    const [customColorAlpha, setCustomColorAlpha] = useState(100);
    const [customGradientFrom, setCustomGradientFrom] = useState('#ff0000');
    const [customGradientTo, setCustomGradientTo] = useState('#0000ff');
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
            const rawWidth = ((e.clientX - blockRect.left) / containerRect.width) * 100;
            // Snap to 10% increments for snappy feel
            const snappedWidth = Math.round(rawWidth / 10) * 10;
            const clampedWidth = Math.max(10, Math.min(100, snappedWidth));

            // Only update if the snapped value changed
            if (clampedWidth !== block.style.widthPercent) {
                onStyleChange(block.id, { widthPercent: clampedWidth });
            }
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
    }, [isResizing, block.id, block.style.widthPercent, onStyleChange]);

    // Detect when mouse is near right edge of block
    const handleMouseMoveOnBlock = (e: React.MouseEvent) => {
        if (!blockRef.current) {
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

    const borderStyles = ['none', 'solid', 'dashed', 'dotted', 'double'] as const;
    const bgColors = [
        'transparent',
        'rgba(255,107,107,0.1)',
        'rgba(255,169,77,0.1)',
        'rgba(255,212,59,0.1)',
        'rgba(105,219,124,0.1)',
        'rgba(116,192,252,0.1)',
        'rgba(177,151,252,0.1)',
        'rgba(247,131,172,0.1)',
    ];
    const gradients = [
        '',
        'linear-gradient(135deg, rgba(255,107,107,0.15) 0%, rgba(255,169,77,0.15) 100%)',
        'linear-gradient(135deg, rgba(116,192,252,0.15) 0%, rgba(177,151,252,0.15) 100%)',
        'linear-gradient(135deg, rgba(105,219,124,0.15) 0%, rgba(116,192,252,0.15) 100%)',
        'linear-gradient(135deg, rgba(247,131,172,0.15) 0%, rgba(177,151,252,0.15) 100%)',
        'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(150,150,150,0.1) 100%)',
        'linear-gradient(135deg, rgba(64,224,208,0.15) 0%, rgba(116,192,252,0.15) 100%)',
    ];

    const handleDelete = () => {
        if (confirmDeletions) {
            if (confirm('Are you sure you want to delete this block?')) {
                onDelete(block.id);
            }
        } else {
            onDelete(block.id);
        }
    };

    const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const title = e.target.value;
        setTitleInput(title);
        onStyleChange(block.id, { title: title || undefined });
    };

    const handleAddCustomColor = () => {
        if (customColorInput) {
            const alpha = customColorAlpha / 100;
            const rgba = hexToRgba(customColorInput, alpha);
            onAddCustomColor?.(rgba);
            onStyleChange(block.id, { backgroundColor: rgba, backgroundGradient: '' });
            setShowCustomColorPicker(false);
        }
    };

    const handleAddCustomGradient = () => {
        const gradient = `linear-gradient(135deg, ${customGradientFrom} 0%, ${customGradientTo} 100%)`;
        onAddCustomGradient?.(gradient);
        onStyleChange(block.id, { backgroundGradient: gradient, backgroundColor: '' });
        setShowCustomGradientPicker(false);
    };

    // Helper to convert hex to rgba
    const hexToRgba = (hex: string, alpha: number) => {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r},${g},${b},${alpha})`;
    };

    return (
        <div
            ref={blockRef}
            className={`text-block ${isNearEdge || isResizing ? 'text-block--resizing' : ''} ${
                blockStyle.title ? 'text-block--has-title' : ''
            }`}
            style={getBlockStyles()}
            onMouseMove={handleMouseMoveOnBlock}
            onMouseLeave={handleMouseLeave}
        >
            {/* Block title (legend-style) */}
            {blockStyle.title && <span className='text-block__title'>{blockStyle.title}</span>}

            {/* Width resize handle */}
            {(isNearEdge || isResizing) && (
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
                <button className='text-block__delete-btn' onClick={handleDelete} title='Delete block'>
                    ×
                </button>
            </div>

            {showStyleMenu && (
                <div className='text-block__style-menu' ref={styleMenuRef}>
                    <div className='style-menu__section'>
                        <span className='style-menu__label'>Title</span>
                        <input
                            type='text'
                            className='style-menu__title-input'
                            placeholder='Block title (optional)'
                            value={titleInput}
                            onChange={handleTitleChange}
                        />
                    </div>
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
                            {customColors.map((color, i) => (
                                <button
                                    key={`custom-${i}`}
                                    className={`style-menu__color style-menu__color--custom ${
                                        blockStyle.backgroundColor === color ? 'style-menu__color--active' : ''
                                    }`}
                                    style={{ backgroundColor: color }}
                                    onClick={() =>
                                        onStyleChange(block.id, { backgroundColor: color, backgroundGradient: '' })
                                    }
                                    title={color}
                                />
                            ))}
                            <button
                                className='style-menu__color style-menu__color--add'
                                onClick={() => setShowCustomColorPicker(!showCustomColorPicker)}
                                title='Add custom color'
                            >
                                +
                            </button>
                        </div>
                        {showCustomColorPicker && (
                            <div className='style-menu__custom-picker'>
                                <input
                                    type='color'
                                    value={customColorInput}
                                    onChange={(e) => setCustomColorInput(e.target.value)}
                                />
                                <input
                                    type='range'
                                    min='0'
                                    max='100'
                                    value={customColorAlpha}
                                    onChange={(e) => setCustomColorAlpha(parseInt(e.target.value))}
                                    title='Opacity'
                                />
                                <span className='style-menu__alpha-label'>{customColorAlpha}%</span>
                                <button onClick={handleAddCustomColor}>Add</button>
                            </div>
                        )}
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
                            {customGradients.map((grad, i) => (
                                <button
                                    key={`custom-grad-${i}`}
                                    className={`style-menu__color style-menu__color--gradient style-menu__color--custom ${
                                        blockStyle.backgroundGradient === grad ? 'style-menu__color--active' : ''
                                    }`}
                                    style={{ background: grad }}
                                    onClick={() =>
                                        onStyleChange(block.id, { backgroundGradient: grad, backgroundColor: '' })
                                    }
                                    title='Custom gradient'
                                />
                            ))}
                            <button
                                className='style-menu__color style-menu__color--add'
                                onClick={() => setShowCustomGradientPicker(!showCustomGradientPicker)}
                                title='Add custom gradient'
                            >
                                +
                            </button>
                        </div>
                        {showCustomGradientPicker && (
                            <div className='style-menu__custom-picker style-menu__custom-picker--gradient'>
                                <div className='style-menu__gradient-colors'>
                                    <label>
                                        From:
                                        <input
                                            type='color'
                                            value={customGradientFrom}
                                            onChange={(e) => setCustomGradientFrom(e.target.value)}
                                        />
                                    </label>
                                    <label>
                                        To:
                                        <input
                                            type='color'
                                            value={customGradientTo}
                                            onChange={(e) => setCustomGradientTo(e.target.value)}
                                        />
                                    </label>
                                </div>
                                <div
                                    className='style-menu__gradient-preview'
                                    style={{
                                        background: `linear-gradient(135deg, ${customGradientFrom}, ${customGradientTo})`,
                                    }}
                                />
                                <button onClick={handleAddCustomGradient}>Add</button>
                            </div>
                        )}
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

            <RichTextEditor
                words={block.words}
                formatMode={formatMode}
                selectedColor={selectedColor}
                selectedSize={selectedSize}
                onWordsChange={(newWords) => onWordsChange(block.id, newWords)}
                onAddBlockAfter={() => onAddBlockAfter(block.id)}
                onClearFormatMode={onClearFormatMode}
                placeholder='Click to edit...'
            />
        </div>
    );
};
