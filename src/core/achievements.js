const ACHIEVEMENTS_LIST = [
  { id: 'first_view', title: 'Curious Scholar', description: 'Viewed your first root detail.', condition: (stats) => stats.rootsViewed >= 1 },
  { id: 'lexicon_master', title: 'Lexicon Master', description: 'Viewed 5 roots.', condition: (stats) => stats.rootsViewed >= 5 }, // Smaller for testing
  { id: 'quiz_pro', title: 'Quiz Pro', description: 'Passed a quiz with 100% score.', condition: (stats) => stats.perfectQuizzes >= 1 }
];

export function trackProgress(currentState, eventType) {
  const stats = currentState.stats || { rootsViewed: 0, perfectQuizzes: 0, searches: 0 };
  const unlocked = currentState.unlockedAchievements || [];

  if (eventType === 'VIEW_ROOT') stats.rootsViewed++;
  if (eventType === 'PERFECT_QUIZ') stats.perfectQuizzes++;
  if (eventType === 'SEARCH') stats.searches++;

  const newlyUnlocked = ACHIEVEMENTS_LIST.filter(a => a.condition(stats) && !unlocked.includes(a.id));
  
  return {
    stats,
    unlocked: [...unlocked, ...newlyUnlocked.map(a => a.id)],
    newlyUnlocked: newlyUnlocked
  };
}

export function getUnlockedAchievements(unlockedIds) {
  return ACHIEVEMENTS_LIST.filter(a => unlockedIds.includes(a.id));
}
