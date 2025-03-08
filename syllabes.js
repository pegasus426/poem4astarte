// Funzione migliorata per dividere una parola italiana in sillabe secondo le regole poetiche
function syllabify(word) {
    if (!word) return [];
    word = word.toLowerCase().trim();

    // Rimuovi punteggiatura iniziale e finale
    word = word.replace(/^[.,;:!?'")\-]+/, '').replace(/[.,;:!?'")\-]+$/, '');

    // Se la parola è troppo corta, considerala come un'unica sillaba
    if (word.length <= 2) {
        return [word];
    }

    // Definizione di vocali, dittonghi e trittonghi
    const vowels = 'aeiouàèéìòóùy';
    const diphthongs = ['ia', 'ie', 'io', 'iu', 'ai', 'ei', 'oi', 'ui', 'au', 'eu'];
    const hiatus = ['ìa', 'ìe', 'ìo', 'ùi', 'ùe', 'ùo', 'àe', 'èa', 'èo', 'òe'];
    const triphthongs = ['iai', 'iei', 'uai', 'uei', 'uoi'];

    // Funzione per verificare se una sequenza consonantica è inseparabile
    function isInseparableCluster(str) {
        const clusters = [
            'br', 'cr', 'dr', 'fr', 'gr', 'pr', 'tr', 'vr',
            'bl', 'cl', 'dl', 'fl', 'gl', 'pl', 'tl', 'vl',
            'ch', 'gh', 'gn', 'sc', 'qu'
        ];
        return clusters.some(cluster => str.startsWith(cluster));
    }

    let syllables = [];
    let currentSyllable = "";
    let i = 0;

    while (i < word.length) {
        // Gestione dei gruppi come "qu": se troviamo "qu" in posizione iniziale o altrimenti,
        // consideralo inseparabile
        if (i + 1 < word.length && word.substr(i, 2) === "qu") {
            currentSyllable += "qu";
            i += 2;
            continue;
        }
        
        // Gestione dei trittonghi: controlla se le tre lettere correnti formano un trittongo
        if (i + 2 < word.length) {
            const possibleTriphthong = word.substr(i, 3);
            if (triphthongs.includes(possibleTriphthong)) {
                currentSyllable += possibleTriphthong;
                i += 3;
                continue;
            }
        }

        // Gestione dei dittonghi o hiati
        if (i + 1 < word.length) {
            const pair = word.substr(i, 2);
            if (diphthongs.includes(pair)) {
                // Se è un dittongo, aggiungi entrambe le lettere e salta
                currentSyllable += pair;
                i += 2;
                continue;
            } else if (hiatus.includes(pair)) {
                // Se è un iato, chiudi la sillaba corrente e riparti con la vocale successiva
                currentSyllable += word[i];
                syllables.push(currentSyllable);
                currentSyllable = "";
                i++; // la vocale successiva inizierà la nuova sillaba
                continue;
            }
        }

 

        // Aggiungi il carattere corrente
        currentSyllable += word[i];

        // Se il carattere corrente è vocale (e non è l'ultima lettera), valuta se dividere la sillaba
        if (vowels.includes(word[i]) && i < word.length - 1) {
            // Se la lettera successiva è vocale, allora dividi (salvo casi già gestiti)
            if (vowels.includes(word[i + 1])) {
                syllables.push(currentSyllable);
                currentSyllable = "";
            } else {
                // Se la lettera successiva è una consonante, controlla il contesto
                if (i + 2 < word.length && !vowels.includes(word[i + 1]) && !vowels.includes(word[i + 2])) {
                    // Se c'è un gruppo di due consonanti, controlla se formano cluster inseparabili
                    const cluster = word.substr(i + 1, 2);
                    if (isInseparableCluster(cluster)) {
                        syllables.push(currentSyllable);
                        currentSyllable = "";
                    } else {
                        // Altrimenti, la prima consonante si lega alla vocale corrente
                        syllables.push(currentSyllable + word[i + 1]);
                        i++; // salta la consonante già associata
                        currentSyllable = "";
                    }
                } else if (i + 1 < word.length - 1) {
                    // Consonante singola seguita da vocale: chiudi la sillaba
                    syllables.push(currentSyllable);
                    currentSyllable = "";
                }
            }
        }
        i++;
    }

    if (currentSyllable) {
        syllables.push(currentSyllable);
    }
    return syllables;
}

function isAtonicMonosyllable(word) {
    const atonicMonosyllables = ['e', 'o', 'a', 'il', 'lo', 'la', 'i', 'gli', 'le', 'un', 'di', 'da', 'in', 'con', 'su', 'per', 'tra', 'fra', 'ma', 'né', 'se'];
    return atonicMonosyllables.includes(word.toLowerCase());
}


// Funzione per il conteggio metrico del verso italiano
let verseType = "";
function countMetricSyllables(verse) {
    verse = verse.trim();
    const words = verse.split(/\s+/);
    let grammaticalSyllables = [];
    words.forEach(word => {
        const syllables = syllabify(word);
        grammaticalSyllables = grammaticalSyllables.concat(syllables);
    });
    const grammaticalCount = grammaticalSyllables.length;

    // Inizialmente il conteggio metrico coincide con quello grammaticale
    let metricalCount = grammaticalCount;
    let sinalefiApplied = [];
    let dialefiApplied = [];

    // Applica la sinalefe a livello di sillaba: se l'ultima sillaba della parola corrente termina con una vocale
    // e la prima sillaba della parola successiva inizia con una vocale, riduci il conteggio metrico.
    for (let i = 0; i < words.length - 1; i++) {
        let currentWordClean = words[i].toLowerCase().replace(/[.,;:!?'")\-]+$/, '');
        let nextWordClean = words[i + 1].toLowerCase().replace(/^['"\-(]+/, '');

        const isCurrentAtonic = isAtonicMonosyllable(currentWordClean);
        const isNextAtonic = isAtonicMonosyllable(nextWordClean);
        // Applica sinalefe solo se almeno una parola è tonica
 
      
        let syllCurrent = syllabify(currentWordClean);
        let syllNext = syllabify(nextWordClean);
        if (syllCurrent.length > 0 && syllNext.length > 0) {
            let lastSyl = syllCurrent[syllCurrent.length - 1];
            let firstSyl = syllNext[0];
            // Se l'ultima sillaba termina con vocale e la prima sillaba inizia con vocale, applica sinalefe
            if ( (!isCurrentAtonic || !isNextAtonic) && /[aeiouàèéìòóù]$/.test(lastSyl) && /^[aeiouàèéìòóù]/.test(firstSyl)) {
                metricalCount--;
                sinalefiApplied.push(`${currentWordClean}-${nextWordClean}`);
            }
        }
    }

    // Eventuali gestioni speciali per apostrofi/elisioni (es. "ch'i'", "ch'io") nel contesto dantesco
    for (let i = 0; i < words.length; i++) {
        const word = words[i].toLowerCase();
        if (word.match(/^[cs]h'[ei]/)) {
            if (metricalCount > 11) {
                metricalCount--;
                sinalefiApplied.push(`${word}-elisione speciale`);
            }
        }
    }

    // Rilevazione del pattern degli accenti per adattare la conta ai versi classici
    let accentPattern = detectAccentPattern(words);

    // Adattamento specifico per endecasillabi (ad esempio, versi danteschi)
    if (metricalCount === 10 || metricalCount === 12) {
        if (isLikelyEndecasillabo(words, accentPattern)) {
            verseType = "Endecasillabo";
            metricalCount = 11;
        }
    }

    if (metricalCount === 11 ||
       (metricalCount === 10 && hasEndecasyllaboPattern(accentPattern)) ||
       (metricalCount === 12 && hasEndecasyllaboPattern(accentPattern))) {
        verseType = "Endecasillabo";
        metricalCount = 11;
    } else if (metricalCount === 7 ||
              (metricalCount === 6 && hasSettenarioPattern(accentPattern)) ||
              (metricalCount === 8 && hasSettenarioPattern(accentPattern))) {
        verseType = "Settenario";
        metricalCount = 7;
    } else {
        verseType = classifyVerse(metricalCount);
    }

    return {
        count: metricalCount,
        grammaticalCount: grammaticalCount,
        type: verseType,
        accents: accentPattern,
        sinalefi: sinalefiApplied,
        dialefi: dialefiApplied
    };
}

// Improved function to detect accent patterns
function detectAccentPattern(words) {
    let accentPattern = [];
    let syllableIndex = 0;
    
    // First pass: identify all stressed syllables
    words.forEach(word => {
        const cleanWord = word.toLowerCase().replace(/[.,;:!?'")\-]+$/, '').replace(/^[.,;:!?'")\-]+/, '');
        const syllables = syllabify(cleanWord);
        
        // Skip empty words or pure punctuation
        if (syllables.length === 0) {
            return;
        }
        
        if (syllables.length > 1) {
            // Check if word has explicit accent marks for stress
            if (/[àèéìòóù]/.test(cleanWord)) {
                // Find which syllable contains the accented vowel
                for (let i = 0; i < syllables.length; i++) {
                    if (/[àèéìòóù]/.test(syllables[i])) {
                        accentPattern.push(syllableIndex + i);
                        break;
                    }
                }
            } else if (hasStressedEnding(cleanWord)) {
                // Parola tronca: accento sull'ultima sillaba
                accentPattern.push(syllableIndex + syllables.length - 1);
            } else if (hasStressedAntepenultimate(cleanWord)) {
                // Parola sdrucciola: accento sulla terzultima sillaba
                accentPattern.push(syllableIndex + syllables.length - 3);
            } else {
                // Parola piana: accento sulla penultima sillaba
                accentPattern.push(syllableIndex + syllables.length - 2);
            }
        } else if (syllables.length === 1 && isTonicMonosyllable(cleanWord)) {
            accentPattern.push(syllableIndex);
        }
        
        syllableIndex += syllables.length;
    });
    
    return accentPattern;
}

// Improved function to detect endecasillabo patterns based on rhythmic principles
function hasEndecasyllaboPattern(accentPattern, totalSyllables) {
    // Principal accent on 10th syllable is characteristic of endecasillabi
    const hasPrincipalAccent = accentPattern.includes(10);
    
    // Check for canonical accent patterns of endecasillabi
    // a maiore: accents on 6th and 10th syllables
    const hasAMaiorePattern = accentPattern.includes(6) && hasPrincipalAccent;
    
    // a minore: accents on 4th and 10th syllables
    const hasAMinorePattern = accentPattern.includes(4) && hasPrincipalAccent;
    
    // Additional rhythmic patterns common in Dante and classical Italian poetry
    const hasDantesqueRhythm = 
        (accentPattern.includes(1) && accentPattern.includes(4) && hasPrincipalAccent) ||
        (accentPattern.includes(4) && accentPattern.includes(8) && hasPrincipalAccent) ||
        (accentPattern.includes(3) && accentPattern.includes(6) && hasPrincipalAccent);
    
    // For verses with 9 grammatical syllables that might be endecasillabi
    // Check if there's a missing syllable due to elision or synaloepha not caught
    const isPotentialEndecasillabo = 
        (totalSyllables === 9 || totalSyllables === 10) && 
        (accentPattern.includes(8) || accentPattern.includes(6) || accentPattern.includes(4));
    
    return hasAMaiorePattern || hasAMinorePattern || hasDantesqueRhythm || isPotentialEndecasillabo;
}

// Improved function for setting verse type based on rhythm analysis
function analyzeVerseType(metricalCount, accentPattern, grammaticalCount) {
    // Use rhythmic principles rather than just syllable count
    
    // Check for endecasillabo based on rhythm
    if (hasEndecasyllaboPattern(accentPattern, grammaticalCount) || 
        (metricalCount >= 10 && metricalCount <= 12)) {
        return {
            type: "Endecasillabo",
            adjustedCount: 11
        };
    }
    
    // Check for settenario
    if ((metricalCount === 7) || 
        (metricalCount === 6 && hasSettenarioPattern(accentPattern)) || 
        (metricalCount === 8 && hasSettenarioPattern(accentPattern))) {
        return {
            type: "Settenario",
            adjustedCount: 7
        };
    }
    
    // Default classification based on syllable count
    return {
        type: classifyVerse(metricalCount),
        adjustedCount: metricalCount
    };
}

// Modify countMetricSyllables to use the improved rhythm analysis
function countMetricSyllables(verse) {
    verse = verse.trim();
    const words = verse.split(/\s+/);
    let grammaticalSyllables = [];
    words.forEach(word => {
        const syllables = syllabify(word);
        grammaticalSyllables = grammaticalSyllables.concat(syllables);
    });
    const grammaticalCount = grammaticalSyllables.length;

    // Inizialmente il conteggio metrico coincide con quello grammaticale
    let metricalCount = grammaticalCount;
    let sinalefiApplied = [];
    let dialefiApplied = [];

    // Apply synaloepha (sinalefe)
    for (let i = 0; i < words.length - 1; i++) {
        let currentWordClean = words[i].toLowerCase().replace(/[.,;:!?'")\-]+$/, '');
        let nextWordClean = words[i + 1].toLowerCase().replace(/^['"\-(]+/, '');

        const isCurrentAtonic = isAtonicMonosyllable(currentWordClean);
        const isNextAtonic = isAtonicMonosyllable(nextWordClean);
        
        let syllCurrent = syllabify(currentWordClean);
        let syllNext = syllabify(nextWordClean);
        if (syllCurrent.length > 0 && syllNext.length > 0) {
            let lastSyl = syllCurrent[syllCurrent.length - 1];
            let firstSyl = syllNext[0];
            // Se l'ultima sillaba termina con vocale e la prima sillaba inizia con vocale, applica sinalefe
            if ((!isCurrentAtonic || !isNextAtonic) && /[aeiouàèéìòóù]$/.test(lastSyl) && /^[aeiouàèéìòóù]/.test(firstSyl)) {
                metricalCount--;
                sinalefiApplied.push(`${currentWordClean}-${nextWordClean}`);
            }
        }
    }

    // Add special handling for potential hidden elisions in Dante's verse
    // Look for potential elisions that might not have been caught
    for (let i = 0; i < words.length; i++) {
        const word = words[i].toLowerCase();
        // Check for apostrophes that might signal elision
        if (word.includes("'")) {
            // Check if we need an additional sinalefe that wasn't caught
            if (grammaticalCount === 9 && metricalCount === 9 && sinalefiApplied.length === 0) {
                metricalCount--;
                sinalefiApplied.push(`${word}-elision effect`);
            }
        }
    }

    // Get accent pattern for rhythm analysis
    const accentPattern = detectAccentPattern(words);

    // Use improved rhythm analysis for verse type
    const verseAnalysis = analyzeVerseType(metricalCount, accentPattern, grammaticalCount);
    
    // Apply the results of rhythm analysis
    const verseType = verseAnalysis.type;
    // Only adjust if necessary (for endecasillabi and settenari primarily)
    if (verseAnalysis.adjustedCount !== metricalCount) {
        metricalCount = verseAnalysis.adjustedCount;
    }

    return {
        count: metricalCount,
        grammaticalCount: grammaticalCount,
        type: verseType,
        accents: accentPattern,
        sinalefi: sinalefiApplied,
        dialefi: dialefiApplied,
    };
}
// Verifica se un monosillabo è tonico
function isTonicMonosyllable(word) {
    word = word.toLowerCase().replace(/^[.,;:!?'")\-]+/, '').replace(/[.,;:!?'")\-]+$/, '');
    const tonicMonosyllables = ['me', 'te', 'sé', 'noi', 'voi', 'tu', 'qui', 'qua', 'già', 'giù', 'più', 'sì', 'no', 'su', 'mai', 'chi', 'che', 'do', 're', 'mi', 'fa', 'sol', 'la', 'si', 'va', 'sa', 'sta', 'dà', 'è', 'ho', 'ha', 'so', "po'", 'po'];
    const atonicMonosyllables = ['il', 'lo', 'la', 'i', 'gli', 'le', 'un', 'una', 'di', 'a', 'da', 'in', 'con', 'su', 'per', 'tra', 'fra', 'e', 'o', 'ma', 'né', 'se', 'mi', 'ti', 'si', 'ci', 'vi'];
    if (tonicMonosyllables.includes(word)) {
        return true;
    } else if (atonicMonosyllables.includes(word)) {
        return false;
    }
    return true;
}

// Verifica se una parola ha l'accento sull'ultima sillaba (parola tronca)
function hasStressedEnding(word) {
    word = word.toLowerCase();
    // Rileva accento fonetico (non ortografico) su ultima sillaba
    const syllables = syllabify(word);
    if (syllables.length === 0) return false;
    const lastSyllable = syllables[syllables.length - 1];
    return /[aeiou]/.test(lastSyllable) && !/[aeiou]{2,}/.test(lastSyllable);
}

function hasStressedAntepenultimate(word) {
    const syllables = syllabify(word);
    if (syllables.length < 3) return false;
    // Accento sulla terzultima se la penultima è breve
    return syllables[syllables.length - 3].match(/[aeiou]/);
}
// Verifica se il pattern degli accenti è tipico dell'endecasillabo
function hasEndecasyllaboPattern(accentPattern) {
    if (!accentPattern.includes(9) && !accentPattern.includes(10)) return false;
    return accentPattern.includes(3) || accentPattern.includes(5) || accentPattern.includes(7);
}

// Verifica se il pattern degli accenti è tipico del settenario
function hasSettenarioPattern(accentPattern) {
    return accentPattern.includes(5) || accentPattern.includes(6);
}

// Classifica il tipo di verso in base al numero di sillabe
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

// Funzione per determinare se un verso è probabilmente un endecasillabo
function isLikelyEndecasillabo(words, accentPattern) {
    let containsHiatus = false;
    let hasDantesqueFeatures = false;
    for (const word of words) {
        const lword = word.toLowerCase();
        if (lword.includes("ch'io") || lword.includes("ch'i'") || lword.includes("c'ha") || lword.includes("v'ha")) {
            hasDantesqueFeatures = true;
        }
        if (["io", "ahi", "sua", "mio", "tuo", "fia"].includes(lword)) {
            containsHiatus = true;
        }
    }
    return hasEndecasyllaboPattern(accentPattern) || hasDantesqueFeatures || containsHiatus;
}


// Aggiungere queste funzioni al file syllabes.js

// Funzione per identificare dittonghi, trittonghi e iati in una sillaba
function identifyVowelGroups(syllable) {
    syllable = syllable.toLowerCase();
    
    // Definizione delle strutture vocaliche
    const diphthongs = ['ia', 'ie', 'io', 'iu', 'ai', 'ei', 'oi', 'ui', 'au', 'eu'];
    const hiatus = ['ìa', 'ìe', 'ìo', 'ùi', 'ùe', 'ùo', 'àe', 'èa', 'èo', 'òe', 'aé', 'aò', 'eà', 'eò', 'oa', 'oe', 'ea', 'oa', 'ua'];
    const triphthongs = ['iai', 'iei', 'uai', 'uei', 'uoi'];
    
    // Verifica se contiene un trittongo
    for (const tri of triphthongs) {
        if (syllable.includes(tri)) {
            return { type: 'triphthong', sequence: tri };
        }
    }
    
    // Verifica se contiene un dittongo
    for (const di of diphthongs) {
        if (syllable.includes(di)) {
            // Verifica che non sia parte di un iato
            let isPartOfHiatus = false;
            for (const hi of hiatus) {
                if (syllable.includes(hi) && hi.includes(di)) {
                    isPartOfHiatus = true;
                    break;
                }
            }
            if (!isPartOfHiatus) {
                return { type: 'diphthong', sequence: di };
            }
        }
    }
    
    // Verifica se contiene un iato
    for (const hi of hiatus) {
        if (syllable.includes(hi)) {
            return { type: 'hiatus', sequence: hi };
        }
    }
    
    return { type: 'normal', sequence: '' };
}

// Modifica la funzione syllabify per esportare informazioni sui gruppi vocalici
function syllabifyWithVowelGroups(word) {
    const syllables = syllabify(word);
    
    // Arricchisci le sillabe con informazioni sui gruppi vocalici
    return syllables.map(syll => {
        const vowelGroup = identifyVowelGroups(syll);
        return {
            text: syll,
            vowelGroup: vowelGroup
        };
    });
}

// Aggiungi questa funzione per generare HTML avanzato delle sillabe
function generateSyllablesHTML(syllableObjects) {
    return syllableObjects.map(syllObj => {
        const { text, vowelGroup } = syllObj;
        
        let html = '';
        
        if (vowelGroup.type !== 'normal' && vowelGroup.sequence) {
            // Evidenzia il gruppo vocalico nella sillaba
            const highlightedText = text.replace(
                vowelGroup.sequence, 
                `<span class="vowel-group-highlight">${vowelGroup.sequence}</span>`
            );
            
            let tagClass = 'vowel-tag';
            let tagText = '';
            
            switch(vowelGroup.type) {
                case 'diphthong':
                    tagClass += ' diphthong-tag';
                    tagText = 'D';
                    break;
                case 'triphthong':
                    tagClass += ' triphthong-tag';
                    tagText = 'T';
                    break;
                case 'hiatus':
                    tagClass += ' hiatus-tag';
                    tagText = 'I';
                    break;
            }
            
            html = `<span class="syllable syllable-${vowelGroup.type}" title="${vowelGroup.type}: ${vowelGroup.sequence}">
                ${highlightedText}
                <span class="${tagClass}">${tagText}</span>
            </span>`;
        } else {
            html = `<span class="syllable">${text}</span>`;
        }
        
        return html;
    }).join(' ');
}
//v1