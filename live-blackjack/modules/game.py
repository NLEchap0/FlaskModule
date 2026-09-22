# FUNZIONAMENTO GENERALE DEL GIOCO
# qui si gestisce il ciclo di una mano: inizio, pesca, banco, risultato.
# Le carte sono gestite da modules/cards.py, la memoria è il database
from models.conn import db
from models.model import Player, Game
from modules import cards, events

# punti guadagnati o persi in base al risultato
SCORE_DELTA = {'win': 10, 'draw': 2, 'loss': -5}


# cerca la mano ancora in corso di un giocatore (se esiste)
def active_game(player_id):
    return db.session.scalars(
        db.select(Game).filter_by(player_id=player_id, status='playing')
    ).first()


# trasforma la mano in un dizionario pronto per il JSON
def game_data(game):
    data = {
        'status': game.status,
        'player_hand': game.player_hand,
        'dealer_hand': game.dealer_hand,
        'player_value': cards.hand_value(game.player_hand),
        'dealer_value': cards.hand_value(game.dealer_hand),
    }
    if game.status == 'finished':
        data['outcome'] = game.outcome
        data['delta'] = SCORE_DELTA[game.outcome]
    return data


# inizia una nuova mano: distribuisce le carte e le salva nel database
def start_game(player):
    # se era rimasta una mano a metà (per esempio pagina ricaricata) la cancello
    old = active_game(player.id)
    if old:
        db.session.delete(old)
        db.session.commit()

    game = Game(player_id=player.id)
    game.deck = cards.new_deck()

    # il giocatore riceve 2 carte, il banco 1
    deck = list(game.deck)
    game.player_hand = [deck.pop(), deck.pop()]
    game.dealer_hand = [deck.pop()]
    game.deck = deck

    db.session.add(game)
    db.session.commit()

    # se il giocatore fa subito 21 la mano si chiude da sola
    if cards.hand_value(game.player_hand) == 21:
        dealer_finishes(game)

    return game_data(game)


# il giocatore chiede una carta
def player_draws(game):
    deck = list(game.deck)
    hand = list(game.player_hand)
    hand.append(deck.pop())
    game.deck = deck
    game.player_hand = hand
    db.session.commit()

    value = cards.hand_value(hand)

    # se sballa o fa 21 la mano finisce e tocca al banco
    if value > 21 or value == 21:
        dealer_finishes(game)

    return game_data(game)


# il giocatore si ferma: gioca il banco e si chiude la mano
def player_stands(game):
    dealer_finishes(game)
    return game_data(game)


# il banco completa la sua mano e poi si chiude la partita
def dealer_finishes(game):
    deck = list(game.deck)
    hand = list(game.dealer_hand)
    cards.dealer_turn(hand, deck)
    game.dealer_hand = hand
    game.deck = deck
    finish_game(game)


# chiude la mano: calcola il risultato e aggiorna il punteggio nel database
def finish_game(game):
    game.outcome = cards.winner(game.player_hand, game.dealer_hand)
    game.status = 'finished'

    player = db.session.get(Player, game.player_id)
    delta = SCORE_DELTA[game.outcome]

    player.score = max(0, player.score + delta)
    if game.outcome == 'win':
        player.wins += 1
    elif game.outcome == 'loss':
        player.losses += 1
    else:
        player.draws += 1

    db.session.commit()

    events.broadcast('game_result', {
        'outcome': game.outcome,
        'delta': delta,
        'player': player.to_dict(),
    })
