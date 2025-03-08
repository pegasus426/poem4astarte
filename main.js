// Funzione migliorata per determinare la rima
function getRhyme(word) {
    if (!word) return '';

    // Rimuovi punteggiatura e normalizza
    word = word.toLowerCase().trim().replace(/[.,;:!?'"\-)+]+$/, '');

    // Se la parola è troppo corta, usa l'intera parola
    if (word.length <= 3) {
        return word;
    }

    const vowels = 'aeiouàèéìòóù';

    // In italiano, le rime tipicamente iniziano dall'ultima vocale accentata

    // Trova l'ultima vocale
    let lastVowelIndex = -1;
    for (let i = word.length - 1; i >= 0; i--) {
        if (vowels.includes(word[i])) {
            lastVowelIndex = i;
            break;
        }
    }

    if (lastVowelIndex === -1) return word; // Nessuna vocale trovata

    // Trova la penultima vocale (per determinare la sillaba accentata)
    let penultimateVowelIndex = -1;
    for (let i = lastVowelIndex - 1; i >= 0; i--) {
        if (vowels.includes(word[i])) {
            penultimateVowelIndex = i;
            break;
        }
    }

    // Se la parola è breve o monosillabica, usa l'intera parola
    if (word.length <= 3 || penultimateVowelIndex === -1) {
        return word;
    }

    // Prendi la parte finale della parola dalla penultima vocale
    return word.slice(penultimateVowelIndex);
}

// Funzione per generare un colore basato su una stringa
function stringToColor(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }

    const hue = Math.abs(hash % 360);
    return `hsl(${hue}, 70%, 40%)`;
}

// Sostituisci la funzione analyzePoetry nel file main.js con questa versione aggiornata

function analyzePoetry() {
    const poetryText = document.getElementById('poetry-text').value;
    const analysisResults = document.getElementById('analysis-results');
    const legendContent = document.getElementById('legend-content');
    const schemeContent = document.getElementById('scheme-content');
    const vowelLegendContent = document.getElementById('vowel-legend-content');

    if (!poetryText.trim()) {
        analysisResults.innerHTML = '<p>Inserisci una poesia da analizzare.</p>';
        return;
    }

    const verses = poetryText.split('\n').filter(verse => verse.trim());

    if (verses.length === 0) {
        analysisResults.innerHTML = '<p>Inserisci almeno un verso.</p>';
        return;
    }

    // Analizza le rime e trova i pattern
    const rhymes = verses.map(verse => {
        const words = verse.trim().split(/\s+/);
        const lastWord = words[words.length - 1];
        return getRhyme(lastWord);
    });

    // Crea un map delle rime uniche
    const uniqueRhymes = [...new Set(rhymes)];
    const rhymeScheme = {};
    const rhymeColors = {};

    // Assegna una lettera a ogni rima unica (a, b, c, ...)
    uniqueRhymes.forEach((rhyme, index) => {
        const letter = String.fromCharCode(97 + index); // 97 è il codice ASCII per 'a'
        rhymeScheme[rhyme] = letter;
        rhymeColors[letter] = stringToColor(rhyme);
    });

    // Genera l'output dell'analisi
    let analysisHTML = '';

    // Conteggio strutture vocaliche per statistiche
    let diphthongCount = 0;
    let triphthongCount = 0;
    let hiatusCount = 0;

    verses.forEach((verse, index) => {
        // Analisi sillabica poetica
        const metricAnalysis = countMetricSyllables(verse);

        const words = verse.trim().split(/\s+/);
        const lastWord = words[words.length - 1];
        const rhyme = rhymes[index];
        const rhymeLetter = rhymeScheme[rhyme];
        const rhymeColor = rhymeColors[rhymeLetter];

        // Estrai le sillabe arricchite con informazioni sui gruppi vocalici
        const syllableData = words.map(word => syllabifyWithVowelGroups(word.trim()));

        // Conta le strutture vocaliche in questo verso
        syllableData.forEach(wordSyllables => {
            wordSyllables.forEach(syll => {
                if (syll.vowelGroup.type === 'diphthong') diphthongCount++;
                else if (syll.vowelGroup.type === 'triphthong') triphthongCount++;
                else if (syll.vowelGroup.type === 'hiatus') hiatusCount++;
            });
        });

        // Crea dettagli sull'analisi metrica
        let metricDetails = `${metricAnalysis.count} sillabe metriche, ${metricAnalysis.grammaticalCount} grammaticali`;
        if (metricAnalysis.sinalefi && metricAnalysis.sinalefi.length > 0) {
            metricDetails += `<br><small>(Sinalefi: ${metricAnalysis.sinalefi.join(', ')})</small>`;
        }

        // Visualizzazione avanzata delle sillabe
        const syllablesHTML = syllableData.map(wordSyllables => {
            return generateSyllablesHTML(wordSyllables);
        }).join(' ');

        analysisHTML += `
        <div class="verse-analysis" data-rhyme="${rhymeLetter}">
            <div class="verse-original">${verse.trim()}
                <span class="rhyme-tag" style="background-color: ${rhymeColor};">${rhymeLetter}</span>
            </div>
            <div class="verse-syllables">
                ${syllablesHTML}
            </div>
            <div class="verse-meter">
                ${metricAnalysis.type} (${metricDetails})
            </div>
            <div class="debug-info">Rima: "${rhyme}" (dalla parola "${lastWord}")</div>
        </div>
    `;
    });

    // Genera la legenda delle rime
    let legendHTML = '';
    for (const letter in rhymeColors) {
        // Trova la rima associata a questa lettera
        const rhymeSound = uniqueRhymes[letter.charCodeAt(0) - 97];
        legendHTML += `
        <div class="legend-item" data-rhyme="${letter}">
            <span class="rhyme-tag" style="background-color: ${rhymeColors[letter]};">${letter}</span>
            <span>"${rhymeSound}"</span>
        </div>
    `;
    }

    // Crea lo schema di rime
    const schemePattern = rhymes.map(rhyme => rhymeScheme[rhyme]).join('');
    let schemeHTML = `
    <div class="schema-display">
        ${Array.from(schemePattern).map(letter =>
        `<span class="schema-letter" data-rhyme="${letter}" style="color: ${rhymeColors[letter]};">${letter}</span>`
    ).join('')}
    </div>
`;

    // Crea la legenda dei gruppi vocalici
    let vowelLegendHTML = `
    <div class="vowel-statistics">
        <p>Statistiche delle strutture vocaliche:</p>
        <div class="vowel-stat"><span class="vowel-tag diphthong-tag">D</span> Dittonghi: ${diphthongCount}</div>
        <div class="vowel-stat"><span class="vowel-tag triphthong-tag">T</span> Trittonghi: ${triphthongCount}</div>
        <div class="vowel-stat"><span class="vowel-tag hiatus-tag">I</span> Iati: ${hiatusCount}</div>
    </div>
`;

    // Aggiorna i risultati
    analysisResults.innerHTML = analysisHTML;
    legendContent.innerHTML = legendHTML;
    schemeContent.innerHTML = schemeHTML;
    vowelLegendContent.innerHTML = vowelLegendHTML;

    // Aggiungi effetto hover per evidenziare le rime e i gruppi vocalici
    setupRhymeHighlighting();
    setupVowelGroupHighlighting();
}

// Nuova funzione per gestire l'hover sui gruppi vocalici
function setupVowelGroupHighlighting() {
    const syllables = document.querySelectorAll('.syllable-diphthong, .syllable-triphthong, .syllable-hiatus');

    syllables.forEach(syll => {
        syll.addEventListener('mouseenter', function () {
            const type = this.classList.contains('syllable-diphthong') ? 'diphthong' :
                this.classList.contains('syllable-triphthong') ? 'triphthong' : 'hiatus';

            highlightVowelGroups(type);
        });

        syll.addEventListener('mouseleave', function () {
            resetVowelHighlights();
        });
    });
}

// Funzione per evidenziare tutti i gruppi vocalici dello stesso tipo
function highlightVowelGroups(type) {
    const syllables = document.querySelectorAll(`.syllable-${type}`);
    syllables.forEach(syll => {
        syll.classList.add('highlight-vowel-group');
    });
}

// Funzione per rimuovere l'evidenziazione dei gruppi vocalici
function resetVowelHighlights() {
    const syllables = document.querySelectorAll('.syllable-diphthong, .syllable-triphthong, .syllable-hiatus');
    syllables.forEach(syll => {
        syll.classList.remove('highlight-vowel-group');
    });
}
// Funzione per configurare l'evidenziazione delle rime al passaggio del mouse
function setupRhymeHighlighting() {
    // Aggiungi effetto hover ai versi
    const verses = document.querySelectorAll('.verse-analysis');
    verses.forEach(verse => {
        verse.addEventListener('mouseenter', function () {
            const rhymeType = this.getAttribute('data-rhyme');
            highlightRhymes(rhymeType);
        });

        verse.addEventListener('mouseleave', function () {
            resetHighlights();
        });
    });

    // Aggiungi effetto hover agli elementi della legenda e dello schema
    const legendItems = document.querySelectorAll('.legend-item, .schema-letter');
    legendItems.forEach(item => {
        item.addEventListener('mouseenter', function () {
            const rhymeType = this.getAttribute('data-rhyme');
            highlightRhymes(rhymeType);
        });

        item.addEventListener('mouseleave', function () {
            resetHighlights();
        });
    });
}

// Funzione per evidenziare le rime dello stesso tipo
function highlightRhymes(rhymeType) {
    const verses = document.querySelectorAll(`.verse-analysis[data-rhyme="${rhymeType}"]`);
    verses.forEach(verse => {
        verse.classList.add('highlight-rhyme');
        const rhymeColor = verse.querySelector('.rhyme-tag').style.backgroundColor;
        verse.style.borderLeftColor = rhymeColor;
    });

    // Evidenzia anche le lettere dello schema
    const schemaLetters = document.querySelectorAll(`.schema-letter[data-rhyme="${rhymeType}"]`);
    schemaLetters.forEach(letter => {
        letter.style.transform = 'scale(1.5)';
        letter.style.textDecoration = 'underline';
    });
}

// Funzione per rimuovere l'evidenziazione
function resetHighlights() {
    const verses = document.querySelectorAll('.verse-analysis');
    verses.forEach(verse => {
        verse.classList.remove('highlight-rhyme');
        verse.style.borderLeftColor = '';
    });

    const schemaLetters = document.querySelectorAll('.schema-letter');
    schemaLetters.forEach(letter => {
        letter.style.transform = '';
        letter.style.textDecoration = '';
    });
}

loadPoem();
// Event listeners
document.getElementById('analyze-btn').addEventListener('click', analyzePoetry);

document.getElementById('poetry-text').addEventListener('keyup', function (event) {
    const poem = document.getElementById('poetry-text').value;
    analyzePoetry();
    savePoem(poem);
});

document.getElementById('poetry-text').addEventListener('paste', function () {
    const poem = document.getElementById('poetry-text').value;
    analyzePoetry();
    savePoem(poem);
});
function savePoem(poem) {
    localStorage.setItem('poem', poem);
}

function loadPoem() {
    const poem = localStorage.getItem('poem');
    if (poem) {
        document.getElementById('poetry-text').value = poem;
        analyzePoetry();
    }
}
document.getElementById('clear-btn').addEventListener('click', function () {
    document.getElementById('poetry-text').value = '';
    document.getElementById('analysis-results').innerHTML = '<p>L\'analisi apparirà qui dopo aver inserito una poesia e cliccato su "Analizza".</p>';
    document.getElementById('legend-content').innerHTML = '';
    document.getElementById('scheme-content').innerHTML = '';
});

// Esempi
document.getElementById('example1').addEventListener('click', function () {
    document.getElementById('poetry-text').value = `Tanto gentile e tanto onesta pare
la donna mia, quand'ella altrui saluta,
ch'ogne lingua devèn, tremando, muta,
e li occhi no l'ardiscon di guardare.

Ella si va, sentendosi laudare,
benignamente e d'umiltà vestuta,
e par che sia una cosa venuta
da cielo in terra a miracol mostrare.`;
    analyzePoetry();
});

document.getElementById('example2').addEventListener('click', function () {
    document.getElementById('poetry-text').value = `Chiare, fresche e dolci acque,
ove le belle membra
pose colei che sola a me par donna;
gentil ramo ove piacque
(con sospir mi rimembra)
a lei di fare al bel fianco colonna;
erba e fior che la gonna
leggiadra ricoverse
co l'angelico seno;
aere sacro, sereno,
ove Amor co' begli occhi il cor m'aperse:
date udienza insieme
a le dolenti mie parole estreme.`;
    analyzePoetry();
});

document.getElementById('example3').addEventListener('click', function () {
    document.getElementById('poetry-text').value = `Nel mezzo del cammin di nostra vita
mi ritrovai per una selva oscura,
ché la diritta via era smarrita.

Ahi quanto a dir qual era è cosa dura
esta selva selvaggia e aspra e forte
che nel pensier rinova la paura!

Tant'è amara che poco è più morte;
ma per trattar del ben ch'i' vi trovai,
dirò de l'altre cose ch'i' v'ho scorte.`;
    analyzePoetry();
});
//v1