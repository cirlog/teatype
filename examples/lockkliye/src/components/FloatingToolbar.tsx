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

// Types
import { FORMAT_COLORS, tFormatMode } from '@/types';

interface iFloatingToolbarProps {
    formatMode: tFormatMode;
    selectedColor: string;
    onFormatModeChange: (mode: tFormatMode) => void;
    onColorChange: (color: string) => void;
}

interface iToolButton {
    mode: tFormatMode;
    icon: string;
    label: string;
    shortcut?: string;
}

const tools: iToolButton[] = [
    { mode: 'bold', icon: 'B', label: 'Bold', shortcut: 'Ctrl+B' },
    { mode: 'italic', icon: 'I', label: 'Italic', shortcut: 'Ctrl+I' },
    { mode: 'underline', icon: 'U', label: 'Underline', shortcut: 'Ctrl+U' },
    { mode: 'strikethrough', icon: 'S', label: 'Strikethrough', shortcut: 'Ctrl+Shift+S' },
    { mode: 'larger', icon: 'A+', label: 'Larger', shortcut: 'Ctrl+]' },
    { mode: 'smaller', icon: 'A-', label: 'Smaller', shortcut: 'Ctrl+[' },
    { mode: 'color', icon: '◉', label: 'Text Color', shortcut: 'Ctrl+Shift+C' },
    { mode: 'highlight', icon: '◌', label: 'Highlight', shortcut: 'Ctrl+Shift+H' },
];

const FloatingToolbar: React.FC<iFloatingToolbarProps> = (props) => {
    return (
        <div className='floating-toolbar'>
            <div className='floating-toolbar__inner'>
                <div className='floating-toolbar__tools'>
                    {tools.map((tool) => (
                        <button
                            key={tool.mode}
                            className={`floating-toolbar__btn ${
                                formatMode === tool.mode ? 'floating-toolbar__btn--active' : ''
                            }`}
                            onClick={() => onFormatModeChange(formatMode === tool.mode ? null : tool.mode)}
                            title={`${tool.label}${tool.shortcut ? ` (${tool.shortcut})` : ''}`}
                            style={tool.mode === 'color' ? { color: selectedColor } : undefined}
                        >
                            <span
                                className={`floating-toolbar__icon ${
                                    tool.mode === 'bold' ? 'floating-toolbar__icon--bold' : ''
                                } ${tool.mode === 'italic' ? 'floating-toolbar__icon--italic' : ''} ${
                                    tool.mode === 'underline' ? 'floating-toolbar__icon--underline' : ''
                                } ${tool.mode === 'strikethrough' ? 'floating-toolbar__icon--strike' : ''}`}
                            >
                                {tool.icon}
                            </span>
                        </button>
                    ))}
                </div>

                <div className='floating-toolbar__divider' />

                <div className='floating-toolbar__colors'>
                    {FORMAT_COLORS.map((color) => (
                        <button
                            key={color}
                            className={`floating-toolbar__color ${
                                selectedColor === color ? 'floating-toolbar__color--active' : ''
                            }`}
                            style={{ backgroundColor: color }}
                            onClick={() => onColorChange(color)}
                            title={`Color: ${color}`}
                        />
                    ))}
                </div>

                <div className='floating-toolbar__divider' />

                <div className='floating-toolbar__status'>
                    {formatMode ? (
                        <span className='floating-toolbar__mode-label'>
                            Mode: <strong>{formatMode}</strong>
                            <span className='floating-toolbar__hint'> (ESC to exit)</span>
                        </span>
                    ) : (
                        <span className='floating-toolbar__hint'>Click tool or use shortcuts</span>
                    )}
                </div>
            </div>
        </div>
    );
};

export default FloatingToolbar;
