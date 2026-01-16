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
import { TeaTag } from './TeaTag';

// Style
import './style/TeaTags.scss';

interface iTeaTagsProps {
    className?: string;
    tags: string[];
}

const TeaTags: React.FC<iTeaTagsProps> = ({ className, tags }) => {
    if (!tags || tags.length === 0) return null;

    return (
        <div className={`tea-tags${className ? ` ${className}` : ''}`}>
            {tags.map((tag, index) => (
                <TeaTag key={index}>{tag}</TeaTag>
            ))}
        </div>
    );
};

export default TeaTags;

export { TeaTags };
