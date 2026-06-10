/**
 * @file data.js
 * @description Data loading and schema migration logic
 */

import { updateState } from './state.js';

export async function loadAppData() {
  try {
    const [appResp, freqResp, pidxResp] = await Promise.all([
      fetch('src/app_data.json'),
      fetch('src/dcs_freq.json').catch(() => null),
      fetch('src/participle_index.json').catch(() => null)
    ]);
    const data = await appResp.json();
    const migrated = migrateAppDataSchema(data);

    // Optional DCS corpus enrichment (sidecar; app works without it)
    if (freqResp && freqResp.ok) {
      try {
        const freq = await freqResp.json();
        mergeDcsFreq(migrated, freq);
      } catch (e) {
        console.warn('DCS frequency sidecar present but unreadable:', e);
      }
    }

    // Optional participle -> root lookup index
    if (pidxResp && pidxResp.ok) {
      try {
        const pidx = await pidxResp.json();
        migrated.participleIndex = pidx.index || {};
        migrated.participleLabels = (pidx.metadata && pidx.metadata.labels) || {};
      } catch (e) {
        console.warn('Participle index present but unreadable:', e);
      }
    }

    updateState({ data: migrated, isLoading: false });
  } catch (error) {
    console.error('Failed to load app data:', error);
    updateState({ isLoading: false });
  }
}

export function mergeDcsFreq(data, freq) {
  if (!freq || !freq.entries) return data;
  data.dcsMeta = freq.metadata || null;
  data.lexicon.forEach(item => {
    const d = freq.entries[item.id];
    if (d) item.dcs = d;
  });
  return data;
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
