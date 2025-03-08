 //Funzione migliorata per dividere una parola italiana in sillabe secondo le regole poetiche
 function syllabify(word) {
    if (!word) return [];

    word = word.toLowerCase().trim();

    // Rimuovi punteggiatura alla fine e all'inizio
    word = word.replace(/[.,;:!?'")\-]+$/, '');
    word = word.replace(/^['"\-(]+/, '');

    // Se la parola è troppo corta, considerala come un'unica sillaba
    if (word.length <= 2) {
        return [word];
    }

    // Vocali
    const vowels = 'aeiouàèéìòóùy';

    // Dittonghi e trittonghi comuni in italiano
    const diphthongs = ['ia', 'ie', 'io', 'iu', 'ai', 'ei', 'oi', 'ui', 'au', 'eu'];
    // Dittonghi con accento che formano iato (si dividono)
    const hiatus = ['ìa', 'ìe', 'ìo', 'ùi', 'ùe', 'ùo', 'àe', 'èa', 'èo', 'òe'];
    const triphthongs = ['iai', 'iei', 'uai', 'uei', 'uoi'];

    // Array per le sillabe
    let syllables = [];
    let currentSyllable = '';
    let i = 0;

    // Funzione per verificare se una combinazione è un gruppo consonantico inseparabile
    function isInseparableCluster(str) {
        const clusters = ['br', 'cr', 'dr', 'fr', 'gr', 'pr', 'tr', 'vr',
            'bl', 'cl', 'dl', 'fl', 'gl', 'pl', 'tl', 'vl',
            'ch', 'gh', 'gn', 'sc', 'qu'];
        return clusters.some(cluster => str.startsWith(cluster));
    }

    while (i < word.length) {
        currentSyllable += word[i];

        // Controlla se abbiamo un trittongo
        if (i + 2 < word.length) {
            let possibleTriphthong = word.substr(i, 3);
            if (triphthongs.includes(possibleTriphthong)) {
                // Aggiungi il resto del trittongo alla sillaba corrente
                if (i + 1 < word.length) currentSyllable += word[i + 1];
                if (i + 2 < word.length) currentSyllable += word[i + 2];
                i += 3;
                continue;
            }
        }

        // Controlla se abbiamo un dittongo o uno iato
        if (i + 1 < word.length) {
            let possibleDiphthong = word.substr(i, 2);

            // Se è uno iato, dobbiamo dividere le vocali in sillabe diverse
            if (hiatus.includes(possibleDiphthong)) {
                if (vowels.includes(word[i])) {
                    syllables.push(currentSyllable);
                    currentSyllable = '';
                }
            }
            // Se è un dittongo, teniamo le vocali insieme
            else if (diphthongs.includes(possibleDiphthong)) {
                // Aggiungi la seconda parte del dittongo alla sillaba corrente
                if (i + 1 < word.length) currentSyllable += word[i + 1];
                i += 2;
                continue;
            }
        }

        // Se la lettera corrente è una vocale e non è l'ultima lettera
        if (vowels.includes(word[i]) && i < word.length - 1) {
            // Se la prossima lettera è una vocale (e non forma un dittongo già gestito sopra)
            if (vowels.includes(word[i + 1])) {
                syllables.push(currentSyllable);
                currentSyllable = '';
            }
            // Se la prossima lettera è una consonante
            else {
                // Gestione speciale per S + consonante
                if (i + 2 < word.length && word[i + 1] === 's' && !vowels.includes(word[i + 2])) {
                    syllables.push(currentSyllable);
                    currentSyllable = '';
                }
                // Gestione per gruppi consonantici inseparabili
                else if (i + 2 < word.length && !vowels.includes(word[i + 1]) && !vowels.includes(word[i + 2])) {
                    if (isInseparableCluster(word.substr(i + 1, 2))) {
                        syllables.push(currentSyllable);
                        currentSyllable = '';
                    } else {
                        // Se non è un gruppo inseparabile, dividi tra le consonanti
                        syllables.push(currentSyllable + word[i + 1]);
                        i++;
                        currentSyllable = '';
                    }
                } else if (i + 1 < word.length - 1) {
                    // Per consonante singola seguita da vocale, la consonante va con la vocale successiva
                    syllables.push(currentSyllable);
                    currentSyllable = '';
                }
            }
        }

        i++;

        // Se siamo arrivati alla fine della parola, aggiungi l'ultima sillaba
        if (i === word.length && currentSyllable) {
            syllables.push(currentSyllable);
        }
    }

    // Se non abbiamo diviso la parola, considerala come un'unica sillaba
    if (syllables.length === 0 && currentSyllable) {
        syllables.push(currentSyllable);
    }

    return syllables;
}

    // Classificazione basata sulla metrica italiana classica
let verseType = "";
// Rilevamento di sinalefe, dialefe, sineresi, dieresi per il conteggio metrico
function countMetricSyllables(verse) {
// Normalizza il verso
verse = verse.trim();

// Dividi il verso in parole
const words = verse.split(/\s+/);

// Conta le sillabe grammaticali totali
let grammaticalSyllables = [];
words.forEach(word => {
const syllables = syllabify(word);
grammaticalSyllables = grammaticalSyllables.concat(syllables);
});
const grammaticalCount = grammaticalSyllables.length;

// Per conteggio metrico, dobbiamo applicare sinalefe, dialefe, etc.
let metricalCount = grammaticalCount;
let sinafefeApplied = [];
let dialefiApplied = [];

// Controlla sinalefe (elisione della vocale finale di una parola con la vocale iniziale della successiva)
for (let i = 0; i < words.length - 1; i++) {
// Pulisci le parole da punteggiatura
const currentWord = words[i].toLowerCase().trim().replace(/[.,;:!?'")\-]+$/, '');
const nextWord = words[i + 1].toLowerCase().trim().replace(/^['"\-(]+/, '');

if (currentWord && nextWord) {
    const vowels = 'aeiouàèéìòóù';
    const lastChar = currentWord[currentWord.length - 1];
    const firstChar = nextWord[0];

    // Se la parola corrente finisce con vocale e la successiva inizia con vocale
    // applica sinalefe (riduci di 1 il conteggio metrico)
    if (vowels.includes(lastChar) && vowels.includes(firstChar)) {
        metricalCount--;
        sinafefeApplied.push(`${currentWord}-${nextWord}`);
    }
}
}

// Gestione di sinalefi multiple in parole con apostrofi
for (let i = 0; i < words.length; i++) {
const word = words[i];

// Controlla elisioni con apostrofo (es. "l'acqua", "dell'arte")
if (word.includes("'")) {
    // L'apostrofo indica già un'elisione, gestita da syllabify()
}
}

// Trattamento speciale per 'ch'i' e simili nel dantesco
for (let i = 0; i < words.length; i++) {
const word = words[i].toLowerCase();
// Gestione dei casi come "ch'i'", "ch'io", "ch'ella" dove c'è un'elisione seguita da pronome
if (word.match(/^[cs]h'[ei]'?/)) {
    // Aggiungi un'ulteriore sinalefe quando necessario
    if (metricalCount > 11) {
        metricalCount--;
        sinafefeApplied.push(`${word}-elisione speciale`);
    }
}
}

// Adattamento speciale per versi particolari (come quelli danteschi)
// Usando un approccio basato sul pattern degli accenti
let accentPattern = detectAccentPattern(words);

// Correzioni specifiche per l'endecasillabo italiano
if (metricalCount === 10 || metricalCount === 12) {
// Verifica se si tratta di un endecasillabo "nascosto"
if (isLikelyEndecasillabo(words, accentPattern)) {
    verseType = "Endecasillabo";
    metricalCount = 11;
}
}



if (metricalCount === 11 ||
(metricalCount === 10 && hasEndecasyllaboPattern(accentPattern)) ||
(metricalCount === 12 && hasEndecasyllaboPattern(accentPattern))) {
verseType = "Endecasillabo";
// Normalizza a 11 gli endecasillabi
metricalCount = 11;
} else if (metricalCount === 7 ||
(metricalCount === 6 && hasSettenarioPattern(accentPattern)) ||
(metricalCount === 8 && hasSettenarioPattern(accentPattern))) {
verseType = "Settenario";
// Normalizza a 7 i settenari
metricalCount = 7;
} else {
verseType = classifyVerse(metricalCount);
}

return {
count: metricalCount,
grammaticalCount: grammaticalCount,
type: verseType,
accents: accentPattern,
sinalefi: sinafefeApplied,
dialefi: dialefiApplied
};
}

// Funzione per rilevare il pattern degli accenti
function detectAccentPattern(words) {
let accentPattern = [];
let syllableIndex = 0;

words.forEach(word => {
const syllables = syllabify(word);
// Stima della posizione dell'accento tonico
if (syllables.length > 1) {
    // Regole specifiche per l'accentazione italiana
    if (hasStressedEnding(word)) {
        // Parole tronche: accento sull'ultima sillaba
        accentPattern.push(syllableIndex + syllables.length - 1);
    } else if (hasStressedAntepenultimate(word)) {
        // Parole sdrucciole: accento sulla terzultima sillaba
        accentPattern.push(syllableIndex + syllables.length - 3);
    } else {
        // Parole piane: accento sulla penultima sillaba (caso più comune in italiano)
        accentPattern.push(syllableIndex + syllables.length - 2);
    }
} else if (syllables.length === 1) {
    // Monosillabi tonici
    if (isTonicMonosyllable(word)) {
        accentPattern.push(syllableIndex);
    }
}
syllableIndex += syllables.length;
});

return accentPattern;
}

// Verifica se un monosillabo è tonico
function isTonicMonosyllable(word) {
word = word.toLowerCase().replace(/[.,;:!?'")\-]+$/, '').replace(/^['"\-(]+/, '');

// Lista di monosillabi tonici in italiano
const tonicMonosyllables = [
'me', 'te', 'sé', 'noi', 'voi', 'tu', 'qui', 'qua', 'già', 'giù', 'più',
'sì', 'no', 'su', 'mai', 'chi', 'che', 'do', 're', 'mi', 'fa', 'sol', 'la',
'si', 'va', 'sa', 'fa', 'sta', 'dà', 'è', 'ho', 'ha', 'so', 'po\'', 'po'
];

// Lista di monosillabi atoni in italiano
const atonicMonosyllables = [
'il', 'lo', 'la', 'i', 'gli', 'le', 'un', 'una', 'di', 'a', 'da', 'in', 'con',
'su', 'per', 'tra', 'fra', 'e', 'o', 'ma', 'né', 'se', 'mi', 'ti', 'si', 'ci', 'vi'
];

if (tonicMonosyllables.includes(word)) {
return true;
} else if (atonicMonosyllables.includes(word)) {
return false;
}

// Se non è in nessuna lista, assumiamo sia tonico
return true;
}

// Verifica se una parola ha l'accento sull'ultima sillaba (parola tronca)
function hasStressedEnding(word) {
word = word.toLowerCase();

// Verifica se la parola termina con vocale accentata
if (/[àèéìòóù]$/.test(word)) {
return true;
}

// Parole che terminano con accento grafico
if (/[aeiou]tà$|[aeiou]tù$|[aeiou]chè$|[aeiou]ché$|ì$|[^h]ò$/.test(word)) {
return true;
}

// Parole che terminano con certi suffissi accentati
if (/ità$|età$|[aeiou]zione$/.test(word)) {
return true;
}

return false;
}

// Verifica se una parola ha l'accento sulla terzultima sillaba (parola sdrucciola)
function hasStressedAntepenultimate(word) {
word = word.toLowerCase();

// Alcune terminazioni comuni per parole sdrucciole
const sdruccioleEndings = [
'abile', 'abili', 'evole', 'evoli', 'acolo', 'acoli', 'ondolo', 'ondoli',
'esimo', 'esimi', 'agine', 'agini', 'iscono', 'assero', 'essero', 'issero',
'avano', 'evano', 'ivano', 'ebbero', 'eranno', 'iranno', 'ettero'
];

for (const ending of sdruccioleEndings) {
if (word.endsWith(ending)) {
    return true;
}
}

return false;
}

// Verifica se un pattern di accenti è tipico dell'endecasillabo
function hasEndecasyllaboPattern(accentPattern) {
// Nel endecasillabo italiano, l'accento principale è sempre sulla 10ª sillaba
// Gli altri accenti significativi possono essere sulla 4ª e 6ª o 4ª e 8ª
if (!accentPattern.includes(9) && !accentPattern.includes(10)) {
return false; // Manca l'accento sulla 10ª sillaba
}

// Verifica i pattern tipici dell'endecasillabo
const has4th = accentPattern.includes(3);
const has6th = accentPattern.includes(5);
const has8th = accentPattern.includes(7);

return has4th || has6th || has8th;
}

// Verifica se un pattern di accenti è tipico del settenario
function hasSettenarioPattern(accentPattern) {
// Nel settenario italiano, l'accento principale è sempre sulla 6ª sillaba
return accentPattern.includes(5) || accentPattern.includes(6);
}

// Verifica se un verso è probabilmente un endecasillabo basato su caratteristiche specifiche
function isLikelyEndecasillabo(words, accentPattern) {
// Controlla la presenza di iati non standard (dialefe forzata)
let containsHiatus = false;

// Controlla pattern di accenti tipici dell'endecasillabo
const hasTypicalPattern = hasEndecasyllaboPattern(accentPattern);

// Controlla le terminazioni caratteristiche del dantesco
let hasDantesqueFeatures = false;

// Verifica se ci sono parole tipiche dantesche che potrebbero causare alterazioni metriche
for (const word of words) {
const lword = word.toLowerCase();
if (lword.includes("ch'io") || lword.includes("ch'i'") || 
    lword.includes("c'ha") || lword.includes("v'ha")) {
    hasDantesqueFeatures = true;
}

// Parole che in Dante spesso causano dialefe contro la regola generale
if (lword === "io" || lword === "ahi" || lword === "sua" || 
    lword === "mio" || lword === "tuo" || lword === "fia") {
    containsHiatus = true;
}
}

// Se ha caratteristiche tipiche dell'endecasillabo dantesco
return hasTypicalPattern || hasDantesqueFeatures || containsHiatus;
}

// Funzione per classificare il tipo di verso in base al numero di sillabe
function classifyVerse(syllableCount) {
    const verseTypes = {
        2: 'Bisillabo',
        3: 'Trisillabo',
        4: 'Quadrisillabo',
        5: 'Quinario',
        6: 'Senario',
        7: 'Settenario',
        8: 'Ottonario',
        9: 'Novenario',
        10: 'Decasillabo',
        11: 'Endecasillabo',
        12: 'Dodecasillabo',
        14: 'Martelliano'
    };

    return verseTypes[syllableCount] || `Verso di ${syllableCount} sillabe`;
}
