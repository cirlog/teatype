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

import { HSDBBaseAPI, HSDBEntity } from '@teatype/api';

// Ensure client is initialized (configures HSDBBaseAPI)
import './client';

/**
 * Student entity interface
 */
export interface Student extends HSDBEntity {
    name: string;
    age: number;
    gender: 'male' | 'female' | 'other';
    height: number;
    school: string;
    university?: string;
}

/**
 * Student API - extends HSDBBaseAPI for students resource
 * 
 * @example
 * ```typescript
 * // Fetch all students
 * const response = await StudentAPI.fetchAll<Student>();
 * 
 * // Fetch with filters
 * const response = await StudentAPI.fetchAll<Student>({
 *     conditions: [{ field: 'age', operator: 'gte', value: 18 }],
 *     sort: { field: 'name', direction: 'asc' },
 * });
 * 
 * // Use query builder
 * const results = await StudentAPI.query<Student>()
 *     .where('gender', 'eq', 'male')
 *     .gte('age', 18)
 *     .sortBy('name')
 *     .execute();
 * ```
 */
export class StudentAPI extends HSDBBaseAPI {
    static resource = 'students';
}

/**
 * University entity interface
 */
export interface University extends HSDBEntity {
    name: string;
    location?: string;
    founded?: number;
}

/**
 * University API - extends HSDBBaseAPI for universities resource
 */
export class UniversityAPI extends HSDBBaseAPI {
    static resource = 'universities';
}
