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
import { TeaButton, TeaPanel } from '../../../../components';

// Icons
import { ModelsIcon, RoundedSquareIcon } from '../../../../icons';

// Style
import './style/ClientKit.scss';

const LLOREM_IPSUM = 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.';

const ClientKit = () => {
    return (
        <div id='client-kit'>
            <TeaPanel title='Panels' variant='framed'>
                <TeaPanel title='Default Panel'>{LLOREM_IPSUM}</TeaPanel>

                <TeaPanel useTheme title='Colored Default Panel'>
                    {LLOREM_IPSUM}
                </TeaPanel>

                <TeaPanel title='Card Panel' variant='card'>
                    {LLOREM_IPSUM}
                </TeaPanel>

                <TeaPanel useTheme title='Colored Card Panel' variant='card'>
                    {LLOREM_IPSUM}
                </TeaPanel>

                <TeaPanel title='Framed Panel' variant='framed'>
                    {LLOREM_IPSUM}
                </TeaPanel>
            </TeaPanel>

            <TeaPanel title='Buttons' variant='framed'>
                <TeaButton>Default</TeaButton>

                <TeaButton theme='success'>Success</TeaButton>

                <TeaButton theme='filled'>Filled</TeaButton>

                <TeaButton>
                    <RoundedSquareIcon />
                </TeaButton>
            </TeaPanel>
        </div>
    );
};

const ClientKitApp = {
    title: 'Client-Kit',
    path: '/client-kit',
    content: ClientKit,
    longDescription: 'A playground for testing and showcasing client-side components and interactions.',
    shortDescription: 'Client-side Component Kit',
    icon: <ModelsIcon />,
    tags: ['Dev', 'Test'],
};

export default ClientKit;

export { ClientKitApp };
