/**
 * @file data.js
 * @description Data loading and schema migration logic
 */

import { updateState } from './state.js';

export async function loadAppData() {
  try {
    const response = await fetch('src/app_data.json');
    const data = await response.json();
    const migrated = migrateAppDataSchema(data);
    updateState({ data: migrated, isLoading: false });
  } catch (error) {
    console.error('Failed to load app data:', error);
    updateState({ isLoading: false });
  }
}

export function migrateAppDataSchema(data) {
  // Logic from Zalizniakiada v17.6
  if (!data.lexicon) data.lexicon = [];
  if (!data.indices) data.indices = { subjects: [], languages: [], names: [] };
  
  // Ensure every item has a unique ID
  data.lexicon.forEach((item, index) => {
    if (!item.id) item.id = `root_${index}`;
  });

  return data;
}
