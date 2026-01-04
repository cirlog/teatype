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

// Style
import './style/TeaTypeApp.scss';

interface iHeroTagsProps {
    name: string;
    pod: number;
    type: string;
}

const HeroTags = ({ name, pod, type }: iHeroTagsProps) => {
    return (
        <div className='hero__tags'>
            <span className='hero__tag'>{name}</span>
            <span className='hero__tag'>pod {pod}</span>
            <span className='hero__tag'>{type}</span>
        </div>
    );
};

interface iTeaTypeAppProps {
    description?: string;
    eyebrow?: string;
    pod?: number;
    title?: string;
    type?: string;
    unit?: string;
}

const TeaTypeApp: React.FC<iTeaTypeAppProps> = (props) => {
    return (
        <header className='hero'>
            <div className='hero__content'>
                <p className='hero__eyebrow'>{props.eyebrow}</p>
                <h1>{props.title}</h1>
                <p className='hero__lede'>{props.description}</p>
                <HeroTags name={props.unit} pod={props.pod} type={props.type} />
            </div>
        </header>
    );
};

export default TeaTypeApp;

export { TeaTypeApp };
