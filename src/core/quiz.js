/**
 * @file quiz.js
 * @description Quiz engine for WhitneyRoots
 */

export function startQuiz(data, count = 10) {
  if (!data || !data.lexicon || data.lexicon.length === 0) return null;
  
  const questions = [];
  const lexicon = data.lexicon;
  
  for (let i = 0; i < count; i++) {
    const target = lexicon[Math.floor(Math.random() * lexicon.length)];
    const type = Math.random() > 0.5 ? 'ROOT_TO_MEANING' : 'MEANING_TO_ROOT';
    
    // Get 3 random decoys
    const decoys = [];
    while (decoys.length < 3) {
      const decoy = lexicon[Math.floor(Math.random() * lexicon.length)];
      if (decoy.id !== target.id && !decoys.includes(decoy)) {
        decoys.push(decoy);
      }
    }
    
    if (type === 'ROOT_TO_MEANING') {
      questions.push({
        question: `What is the meaning of the root √${target.root}?`,
        options: shuffle([target.meaning, ...decoys.map(d => d.meaning)]),
        answer: target.meaning
      });
    } else {
      questions.push({
        question: `Which root means '${target.meaning}'?`,
        options: shuffle([`√${target.root}`, ...decoys.map(d => `√${d.root}`)]),
        answer: `√${target.root}`
      });
    }
  }
  
  return {
    title: "Dynamic Root Challenge",
    questions,
    score: 0
  };
}

function shuffle(array) {
  return array.sort(() => Math.random() - 0.5);
}
