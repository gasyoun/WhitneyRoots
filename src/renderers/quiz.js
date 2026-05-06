/**
 * @file quiz.js
 * @description Quiz renderer for WhitneyRoots
 */

import { createElement } from '../utils/dom.js';
import { whitneyQuiz, startQuiz } from '../core/quiz.js';
import { updateState } from '../core/state.js';

export function renderQuiz() {
  const quizState = startQuiz(1); // Default to level 1
  const container = createElement('div', { class: 'quiz-container' });
  
  function renderQuestion(questionIndex) {
    container.innerHTML = '';
    const q = quizState.questions[questionIndex];
    
    const questionEl = createElement('div', { class: 'quiz-question' }, [
      createElement('h2', {}, [`Question ${questionIndex + 1}`]),
      createElement('p', { class: 'question-text' }, [q.question]),
      createElement('div', { class: 'options' }, q.options.map(opt => {
        const btn = createElement('button', { class: 'option-btn' }, [opt]);
        btn.onclick = () => {
          if (opt === q.answer) {
            quizState.score++;
            btn.classList.add('correct');
          } else {
            btn.classList.add('wrong');
          }
          
          setTimeout(() => {
            if (questionIndex + 1 < quizState.questions.length) {
              renderQuestion(questionIndex + 1);
            } else {
              renderResult();
            }
          }, 1000);
        };
        return btn;
      }))
    ]);
    
    container.appendChild(questionEl);
  }

  function renderResult() {
    container.innerHTML = '';
    container.appendChild(createElement('div', { class: 'quiz-result' }, [
      createElement('h2', {}, ['Quiz Complete!']),
      createElement('p', {}, [`Your score: ${quizState.score} / ${quizState.questions.length}`]),
      createElement('button', { 
        class: 'back-btn', 
        onclick: () => updateState({ view: 'lexicon' }) 
      }, ['Back to Roots'])
    ]));
  }

  renderQuestion(0);
  return container;
}
