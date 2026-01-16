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
import { TTInfotip } from './TTInfotip';

// Style
import './style/TTApp.scss';

interface iHeroTagsProps {
    name?: string;
    pod?: number;
    type?: string;
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

interface iTTAppProps {
    children: React.ReactNode;
    description?: string;
    flare?: string;
    pod?: number;
    title?: string;
    type?: string;
    unit?: string;
}

const TTApp: React.FC<iTTAppProps> = (props) => {
    return (
        <div id='tt-app'>
            <header>
                <p className='tt-app-flare'>{props.flare}</p>
                <div className='tt-app-title-row'>
                    <h1>{props.title}</h1>
                    {/* {props.description && (
                        <div className='hero__info'>
                            <TTInfotip position='right'>{props.description}</TTInfotip>
                        </div>
                    )} */}
                </div>
                {/* <HeroTags name={props.unit} pod={props.pod} type={props.type} /> */}
            </header>

            <main>{props.children}</main>
        </div>
    );
};

export default TTApp;

export { TTApp };
