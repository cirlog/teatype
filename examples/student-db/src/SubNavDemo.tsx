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
import { useState } from 'react';

// Components
import { TeaSubNav } from '@teatype/components';

// Icons
import { DatabaseIcon, ArrowIcon, SettingsIcon } from '@teatype/icons';

// Styles
import './subnav-demo.scss';

// Demo content components
function OverviewContent() {
    return (
        <div className='demo-content'>
            <h3>Overview</h3>
            <p>
                Welcome to the TeaSubNav component demo. This component provides tab-style subnavigation with elegant
                hover effects.
            </p>
            <ul>
                <li>Hover over tabs to see the animated underline effect</li>
                <li>The selected tab is elevated with a permanent accent border</li>
                <li>Icons appear next to selected tab labels</li>
            </ul>
        </div>
    );
}

function DetailsContent() {
    return (
        <div className='demo-content'>
            <h3>Details</h3>
            <p>The TeaSubNav component features:</p>
            <ul>
                <li>
                    <strong>Hover line effect:</strong> A subtle line appears under all tabs when hovering
                </li>
                <li>
                    <strong>Highlighted section:</strong> The hovered tab's section is in the accent color
                </li>
                <li>
                    <strong>Selection state:</strong> Selected tabs are pushed up with a permanent border
                </li>
                <li>
                    <strong>Icon support:</strong> Optional icons appear when a tab is selected
                </li>
            </ul>
        </div>
    );
}

function SettingsContent() {
    return (
        <div className='demo-content'>
            <h3>Settings</h3>
            <p>Configure the component through props:</p>
            <pre>{`<TeaSubNav
    items={[
        { id: 'overview', label: 'Overview', icon: <ArrowIcon /> },
        { id: 'details', label: 'Details' },
        { id: 'settings', label: 'Settings', icon: <SettingsIcon /> },
    ]}
    selectedId={activeTab}
    onSelect={setActiveTab}
/>`}</pre>
        </div>
    );
}

function AnalyticsContent() {
    return (
        <div className='demo-content'>
            <h3>Analytics</h3>
            <p>Track user navigation patterns and tab usage with the onSelect callback.</p>
        </div>
    );
}

function SubNavDemo() {
    const [activeTab, setActiveTab] = useState('overview');
    const [disabledExampleTab, setDisabledExampleTab] = useState('active1');
    const [minimalExampleTab, setMinimalExampleTab] = useState('tab1');

    const tabs = [
        { id: 'overview', label: 'Overview', icon: <ArrowIcon /> },
        { id: 'details', label: 'Details', icon: <DatabaseIcon /> },
        { id: 'settings', label: 'Settings', icon: <SettingsIcon /> },
        { id: 'analytics', label: 'Analytics', disabled: false },
    ];

    return (
        <div className='subnav-demo'>
            <div className='subnav-demo__section'>
                <h2>Basic Example</h2>
                <TeaSubNav items={tabs} selectedId={activeTab} onSelect={setActiveTab} />

                <div className='subnav-demo__content'>
                    {activeTab === 'overview' && <OverviewContent />}
                    {activeTab === 'details' && <DetailsContent />}
                    {activeTab === 'settings' && <SettingsContent />}
                    {activeTab === 'analytics' && <AnalyticsContent />}
                </div>
            </div>

            <div className='subnav-demo__section'>
                <h2>With Disabled Tab</h2>
                <TeaSubNav
                    items={[
                        { id: 'active1', label: 'Active Tab' },
                        { id: 'active2', label: 'Another Tab' },
                        { id: 'disabled', label: 'Disabled', disabled: true },
                    ]}
                    selectedId={disabledExampleTab}
                    onSelect={setDisabledExampleTab}
                />
            </div>

            <div className='subnav-demo__section'>
                <h2>Minimal Example</h2>
                <TeaSubNav
                    items={[
                        { id: 'tab1', label: 'First' },
                        { id: 'tab2', label: 'Second' },
                    ]}
                    selectedId={minimalExampleTab}
                    onSelect={setMinimalExampleTab}
                />
            </div>
        </div>
    );
}

export default SubNavDemo;
