export function getAIInsights(rootItem) {
  const insights = [];
  
  if (rootItem.classes && rootItem.classes.length > 1) {
    insights.push(`Note: This root belongs to multiple classes (${rootItem.classes.join(', ')}), indicating high morphological versatility.`);
  }
  
  if (rootItem.ppp && rootItem.ppp.length > 2) {
    insights.push(`Philological Tip: Multiple PPP forms suggest varied usage in different Vedic or Classical periods.`);
  }

  if (rootItem.meaning && rootItem.meaning.toLowerCase().includes('go')) {
    insights.push("Comparative Insight: Roots of 'going' often develop abstract meanings like 'knowing' or 'attaining' in Sanskrit.");
  }
  
  return insights.length > 0 ? insights.join(' ') : "Focus on mastering the primary meaning and class first.";
}

export function getPrefixSuggestions(rootItem) {
  // Common Sanskrit prefixes (Upasargas)
  const upasargas = ['pra', 'apa', 'sam', 'anu', 'vi', 'upa', 'ni', 'ati'];
  return upasargas.slice(0, 3).map(u => `${u}-${rootItem.root}`);
}
