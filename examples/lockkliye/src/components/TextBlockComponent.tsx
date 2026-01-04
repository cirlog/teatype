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
}: iTextBlockComponentProps) => {
    const [showStyleMenu, setShowStyleMenu] = useState(false);
    const [isResizing, setIsResizing] = useState(false);
    const [isNearEdge, setIsNearEdge] = useState(false);
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
            className={`text-block ${isNearEdge || isResizing ? 'text-block--resizing' : ''}`}
            style={getBlockStyles()}
            onMouseMove={handleMouseMoveOnBlock}
            onMouseLeave={handleMouseLeave}
        >
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

            <RichTextEditor
                words={block.words}
                formatMode={formatMode}
                selectedColor={selectedColor}
                selectedSize={selectedSize}
                onWordsChange={(newWords) => onWordsChange(block.id, newWords)}
                onAddBlockAfter={() => onAddBlockAfter(block.id)}
                placeholder='Click to edit...'
            />
        </div>
    );
};
