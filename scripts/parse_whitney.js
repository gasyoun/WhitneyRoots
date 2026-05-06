/**
 * @file parse_whitney.js
 * @description Parser for Whitney Roots data into app_data.json
 */

const fs = require('fs');
const path = require('path');

const INPUT_FILE = path.join(__dirname, '../Whitney_roots_class-PP.txt');
const OUTPUT_FILE = path.join(__dirname, '../app_data.json');

function parse() {
  const content = fs.readFileSync(INPUT_FILE, 'utf8');
  const lines = content.split('\n');
  
  const lexicon = [];
  const subjectIndex = {
    "Verb Classes": [],
    "Grammar Concepts": ["Root", "PPP", "Verb Form"]
  };
  
  // Basic cleaning and extraction
  // Format: №  √ корень               Класс(ы)           PPP-форма(ы)                   Значение
  // Example: 11. √ad                    I/II               —                              eat
  
  const classesSet = new Set();

  lines.forEach(line => {
    // Regex to capture: No, Root, Classes, PPP, Meaning
    // We need to be careful with the fixed width or variable spacing
    const match = line.match(/^\s*(\d+)\.\s+(.*?)\s{2,}(.*?)\s{2,}(.*?)\s{2,}(.*)$/);
    if (match) {
      let [_, id, root, classes, ppp, meaning] = match;
      
      root = root.replace('√', '').trim();
      classes = classes.trim();
      ppp = ppp.replace('—', '').trim();
      meaning = meaning.replace(/<!--.*?-->/g, '').trim(); // Remove HTML comments
      
      // Clean up classes
      const classList = classes === '—' ? [] : classes.split('/').map(c => c.trim());
      classList.forEach(c => classesSet.add(c));

      lexicon.push({
        id: `root_${id}`,
        title: root,
        type: "lexicon",
        description: meaning,
        metadata: {
          id: parseInt(id),
          verb_classes: classList,
          ppp: ppp,
          source: "Whitney Roots"
        }
      });
    }
  });

  subjectIndex["Verb Classes"] = Array.from(classesSet).sort();

  const appData = {
    version: "1.0.0-whitney",
    project: "WhitneyRoots",
    lexicon: lexicon,
    subjectIndex: subjectIndex,
    names: [
      { id: "whitney", name: "William Dwight Whitney", description: "Author of 'The Roots, Verb-forms and Primary Derivatives of the Sanskrit Language'." }
    ]
  };

  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(appData, null, 2));
  console.log(`✅ Parsed ${lexicon.length} roots into ${OUTPUT_FILE}`);
}

parse();
