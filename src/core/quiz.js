/**
 * @file quiz.js
 * @description Quiz engine for WhitneyRoots
 */

export const whitneyQuiz = {
  levels: [
    {
      id: 1,
      title: "Basic Roots",
      questions: [
        {
          question: "What is the meaning of the root √ad?",
          options: ["go", "eat", "praise", "be"],
          answer: "eat"
        },
        {
          question: "Which root means 'to breathe'?",
          options: ["√an", "√as", "√ah", "√am"],
          answer: "√an"
        }
      ]
    }
  ]
};

export function startQuiz(levelId) {
  const level = whitneyQuiz.levels.find(l => l.id === levelId);
  if (!level) return null;
  
  return {
    ...level,
    currentQuestion: 0,
    score: 0
  };
}
