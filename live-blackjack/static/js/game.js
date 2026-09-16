// Ogni tab ha un session_id proprio, salvato in sessionStorage (non condiviso tra tab)
let sessionId = sessionStorage.getItem('bj_session_id');
if (!sessionId) {
    sessionId = crypto.randomUUID();
    sessionStorage.setItem('bj_session_id', sessionId);
}

let myPlayer = null;

const el = (id) => document.getElementById(id);

async function api(path, body) {
    const res = await fetch('/api' + path, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body ?? {session_id: sessionId}),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || 'Errore server');
    return data;
}

function cardHtml(card) {
    const red = ['♥', '♦'].includes(card.suit);
    return `<div class="card-slot ${red ? 'red' : ''}" data-corner="${card.rank}${card.suit}">${card.suit}<small>${card.rank}</small></div>`;
}

function renderHands(data) {
    el('player-hand').innerHTML = data.player_hand.map(cardHtml).join('');
    el('dealer-hand').innerHTML = data.dealer_hand.map(cardHtml).join('');
    el('player-value').textContent = data.player_value;
    el('dealer-value').textContent = data.dealer_value;
}

function setButtons(status) {
    const playing = status === 'playing';
    el('hit-btn').disabled = !playing;
    el('stand-btn').disabled = !playing;
    el('new-game-btn').disabled = playing;
}

function showMessage(text, outcome) {
    const box = el('game-message');
    box.className = 'result-banner rb-' + outcome;
    box.textContent = text;
    box.classList.remove('d-none');
}

function hideMessage() {
    el('game-message').classList.add('d-none');
}

function updateMyScore(player) {
    if (!player) return;
    myPlayer = player;
    el('my-score').textContent = player.score;
    el('wl-stats').textContent =
        `${player.wins} vittorie · ${player.draws} pareggi · ${player.losses} sconfitte`;
}

// punteggi precedenti per calcolare il trend (verde = sale, giallo = invariato, rosso = scende)
const lastScores = {};

function renderLeaderboard(players) {
    const me = sessionId;
    el('leaderboard').innerHTML = players.map(p => {
        const classes = [];
        if (p.id === me) classes.push('me');

        // trend: verde se sale, giallo se invariato, rosso se scende
        const prev = lastScores[p.id];
        if (prev === undefined) lastScores[p.id] = p.score;
        else if (p.score > prev) classes.push('trend-up');
        else if (p.score < prev) classes.push('trend-down');
        else classes.push('trend-flat');
        lastScores[p.id] = p.score;

        return `<tr class="${classes.join(' ')}">
            <td>${escapeHtml(p.name)}${p.id === me ? ' (tu)' : ''}</td>
            <td class="score-cell">${p.score}</td>
            <td class="wdl-cell">${p.wins}/${p.draws}/${p.losses}</td>
        </tr>`;
    }).join('');
}

function escapeHtml(s) {
    return s.replace(/[&<>"']/g, c => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
}

async function refreshLeaderboard() {
    const players = await fetch('/api/players').then(r => r.json());
    renderLeaderboard(players);
}

async function join() {
    const name = el('player-name').value.trim() || 'Guest';
    try {
        myPlayer = await api('/players', {session_id: sessionId, name});
        el('join-screen').classList.add('d-none');
        el('game-screen').classList.remove('d-none');
        el('session-info').textContent = `Sessione ${sessionId.slice(0, 8)} · ${name}`;
        updateMyScore(myPlayer);
        await refreshLeaderboard();
    } catch (e) {
        el('join-error').textContent = e.message;
    }
}

async function newGame() {
    hideMessage();
    const data = await api('/game/new');
    renderHands(data);
    setButtons('playing');
}

async function hit() {
    const data = await api('/game/hit');
    renderHands(data);
    if (data.status === 'finished') {
        setButtons('finished');
        endOfHand(data);
    }
}

async function stand() {
    const data = await api('/game/stand');
    renderHands(data);
    setButtons('finished');
    endOfHand(data);
}

function endOfHand(data) {
    const messages = {
        win: `♠ JACKPOT — HAI VINTO! +${data.delta} PUNTI`,
        draw: `✦ PAREGGIO +${data.delta} PUNTI`,
        loss: `✖ HAI PERSO ${Math.abs(data.delta)} PUNTI`,
    };
    showMessage(messages[data.outcome], data.outcome);
    updateMyScore(data.player);
    refreshLeaderboard();
}

// Server-Sent Events: aggiornamenti in tempo reale da tutti gli altri tab/giocatori
function connectEvents() {
    const es = new EventSource('/api/events');
    es.onopen = () => {
        el('conn-status').className = 'conn-badge online';
        el('conn-status').textContent = 'online';
    };
    es.onerror = () => {
        el('conn-status').className = 'conn-badge offline';
        el('conn-status').textContent = 'offline';
    };
    es.onmessage = (e) => {
        const {type, data} = JSON.parse(e.data);
        if (type === 'game_result') {
            if (data.player) renderLeaderboardPush(data.player);
        } else if (type === 'player_joined') {
            renderLeaderboardPush(data);
        } else if (type === 'player_left') {
            delete lastScores[data.id];
            refreshLeaderboard();
        }
    };
}

// quando il tab si chiude (o si ricarica) il giocatore lascia il tavolo e viene eliminato
function announceExit() {
    const payload = JSON.stringify({session_id: sessionId});
    // sendBeacon parte anche durante la chiusura della pagina
    if (navigator.sendBeacon) {
        navigator.sendBeacon('/api/players/leave',
            new Blob([payload], {type: 'application/json'}));
    } else {
        fetch('/api/players/leave', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: payload,
            keepalive: true,
        });
    }
}

window.addEventListener('pagehide', announceExit);

// aggiorna/inserisce un giocatore nella classifica ricevuta via SSE (senza ricaricare tutto)
function renderLeaderboardPush(player) {
    if (player.id === sessionId) updateMyScore(player);
    refreshLeaderboard();
}

el('join-btn').addEventListener('click', join);
el('player-name').addEventListener('keydown', e => { if (e.key === 'Enter') join(); });
el('new-game-btn').addEventListener('click', newGame);
el('hit-btn').addEventListener('click', hit);
el('stand-btn').addEventListener('click', stand);

connectEvents();
