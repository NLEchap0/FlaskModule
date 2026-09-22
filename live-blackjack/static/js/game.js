// la sessione è salvata sul server: qui tengo solo i dati del giocatore
let myPlayer = null;

// chiamata POST alle API
async function api(path, body) {
    const res = await fetch('/api' + path, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body ?? {player_id: myPlayer.id}),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || 'Errore server');
    return data;
}

// HTML di una carta
function cardHtml(card) {
    const red = card.suit === '♥' || card.suit === '♦';
    return `<div class="card-slot ${red ? 'red' : ''}" data-corner="${card.rank}${card.suit}">
        ${card.suit}<small>${card.rank}</small></div>`;
}

function renderHands(data) {
    document.getElementById('player-hand').innerHTML = data.player_hand.map(cardHtml).join('');
    document.getElementById('dealer-hand').innerHTML = data.dealer_hand.map(cardHtml).join('');
    document.getElementById('player-value').textContent = data.player_value;
    document.getElementById('dealer-value').textContent = data.dealer_value;
}

function setButtons(status) {
    const playing = status === 'playing';
    document.getElementById('hit-btn').disabled = !playing;
    document.getElementById('stand-btn').disabled = !playing;
    document.getElementById('new-game-btn').disabled = playing;
}

function showMessage(text, outcome) {
    const box = document.getElementById('game-message');
    box.className = 'result-banner rb-' + outcome;
    box.textContent = text;
}

// svuota il messaggio: il box resta ma diventa invisibile
function hideMessage() {
    const box = document.getElementById('game-message');
    box.className = 'result-banner';
    box.textContent = '';
}

function updateMyScore(player) {
    if (!player) return;
    myPlayer = player;
    document.getElementById('my-score').textContent = player.score;
    document.getElementById('wl-stats').textContent =
        `${player.wins} vittorie · ${player.draws} pareggi · ${player.losses} sconfitte`;
}

function renderLeaderboard(players) {
    document.getElementById('leaderboard').innerHTML = players.map(p => {
        const me = p.id === myPlayer.id ? ' class="me"' : '';
        const nome = p.id === myPlayer.id ? `${p.name} (tu)` : p.name;
        return `<tr${me}>
            <td>${nome}</td>
            <td class="score-cell">${p.score}</td>
            <td class="wdl-cell">${p.wins}/${p.draws}/${p.losses}</td>
        </tr>`;
    }).join('');
}

async function refreshLeaderboard() {
    const res = await fetch('/api/players');
    renderLeaderboard(await res.json());
}

// login: il server crea (o ritrova) il giocatore dal nome
async function join() {
    const name = document.getElementById('player-name').value.trim() || 'Guest';
    try {
        myPlayer = await api('/players', {name: name});
        sessionStorage.setItem('bj_player', JSON.stringify(myPlayer));
        enterTable();
    } catch (e) {
        document.getElementById('join-error').textContent = e.message;
    }
}

// chiude il modale e mostra il tavolo
function enterTable() {
    document.getElementById('join-modal').classList.add('hidden');
    document.getElementById('session-info').textContent = `Sessione #${myPlayer.id} · ${myPlayer.name}`;
    updateMyScore(myPlayer);
    refreshLeaderboard();
}

// nuova mano
async function newGame() {
    hideMessage();
    const data = await api('/game/new');
    renderHands(data);

    // se ho fatto subito 21 la mano è già finita
    if (data.status === 'finished') {
        setButtons('finished');
        endOfHand(data);
    } else {
        setButtons('playing');
    }
}

// chiedo una carta
async function hit() {
    const data = await api('/game/hit');
    renderHands(data);
    if (data.status === 'finished') {
        setButtons('finished');
        endOfHand(data);
    }
}

// mi fermo
async function stand() {
    const data = await api('/game/stand');
    renderHands(data);
    setButtons('finished');
    endOfHand(data);
}

// fine della mano: messaggio e punteggi
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

// eventi in tempo reale dal server per aggiornare la classifica
function connectEvents() {
    const es = new EventSource('/api/events');

    es.onopen = () => {
        document.getElementById('conn-status').className = 'online';
        document.getElementById('conn-status').textContent = 'online';
    };
    es.onerror = () => {
        document.getElementById('conn-status').className = 'offline';
        document.getElementById('conn-status').textContent = 'offline';
    };

    es.onmessage = (e) => {
        const {type, data} = JSON.parse(e.data);
        if (type === 'game_result') {
            if (data.player.id === myPlayer.id) updateMyScore(data.player);
            refreshLeaderboard();
        } else if (type === 'player_joined' || type === 'player_left') {
            refreshLeaderboard();
        }
    };
}

// quando chiudo il tab avviso il server
window.addEventListener('pagehide', () => {
    if (!myPlayer) return;
    fetch('/api/players/leave', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({player_id: myPlayer.id}),
        keepalive: true,
    });
    myPlayer = null;
    sessionStorage.removeItem('bj_player');
});

document.getElementById('join-btn').addEventListener('click', join);
document.getElementById('player-name').addEventListener('keydown', e => {
    if (e.key === 'Enter') join();
});
document.getElementById('new-game-btn').addEventListener('click', newGame);
document.getElementById('hit-btn').addEventListener('click', hit);
document.getElementById('stand-btn').addEventListener('click', stand);

connectEvents();
