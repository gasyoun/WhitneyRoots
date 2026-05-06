export function buildTopicClusters(data) {
  const clusters = {};
  const commonKeywords = ['move', 'speak', 'shine', 'eat', 'go', 'sound', 'be', 'do', 'strike', 'cut'];
  
  data.lexicon.forEach(item => {
    const meaning = item.meaning.toLowerCase();
    commonKeywords.forEach(keyword => {
      if (meaning.includes(keyword)) {
        if (!clusters[keyword]) clusters[keyword] = [];
        clusters[keyword].push(item.id);
      }
    });
  });
  
  return Object.entries(clusters).map(([name, roots]) => ({ name, roots }));
}

export function calculateCentrality(data) {
  // Simple centrality: roots with many PPP forms or multiple classes are "influential"
  const centrality = {};
  data.lexicon.forEach(item => {
    let score = 0;
    if (item.ppp) score += item.ppp.length * 2;
    if (item.classes) score += item.classes.length * 1.5;
    if (item.meaning.length < 15) score += 1; // Short core meanings are often fundamental
    centrality[item.id] = score;
  });
  return centrality;
}
