from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        self._tours_della_regione = []
        self._max_giorni = 0
        self._max_budget = 0

        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):
        relazioni = TourDAO.get_tour_attrazioni()

        for tour in self.tour_map.values():
            tour.attrazioni = set()

        for row in relazioni:
            t_id = row['id_tour']
            a_id = row['id_attrazione']

            if t_id in self.tour_map and a_id in self.attrazioni_map:
                obj_tour = self.tour_map[t_id]
                obj_attrazione = self.attrazioni_map[a_id]
                obj_tour.attrazioni.add(obj_attrazione)


    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):

        self._pacchetto_ottimo = []
        self._costo_ottimo = 0
        self._valore_ottimo = -1

        self._tours_della_regione = [t for t in self.tour_map.values() if t.id_regione == id_regione]

        self._max_giorni = max_giorni if max_giorni is not None else float('inf')
        self._max_budget = max_budget if max_budget is not None else float('inf')

        self._ricorsione(
            start_index=0,
            pacchetto_parziale=[],
            durata_corrente=0,
            costo_corrente=0,
            valore_corrente=0,
            attrazioni_usate=set()
        )

        return self._pacchetto_ottimo, self._costo_ottimo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float,
                    valore_corrente: int, attrazioni_usate: set):

        # 1. Controllo la soluzione parziale
        if valore_corrente > self._valore_ottimo:
            self._valore_ottimo = valore_corrente
            self._pacchetto_ottimo = list(pacchetto_parziale)
            self._costo_ottimo = costo_corrente

        # 2. Terminazione
        if start_index >= len(self._tours_della_regione):
            return

        tour_corrente = self._tours_della_regione[start_index]

        # Vincoli:
        # Budget non superato
        # Durata non superata
        # Attrazioni uniche (intersezione tra le attrazioni del tour e quelle già usate deve essere vuota)

        nuovo_costo = costo_corrente + tour_corrente.costo
        nuova_durata = durata_corrente + tour_corrente.durata_giorni

        # Verifico intersezione
        is_attrazioni_duplicate = not tour_corrente.attrazioni.isdisjoint(attrazioni_usate)

        if (nuovo_costo <= self._max_budget and
                nuova_durata <= self._max_giorni and
                not is_attrazioni_duplicate):
            # Nuovo valore culturale
            valore_tour = sum(a.valore_culturale for a in tour_corrente.attrazioni)
            pacchetto_parziale.append(tour_corrente)

            # NUOVO set unito per evitare modifiche all'originale
            nuove_attrazioni_usate = attrazioni_usate.union(tour_corrente.attrazioni)

            self._ricorsione(
                start_index + 1,
                pacchetto_parziale,
                nuova_durata,
                nuovo_costo,
                valore_corrente + valore_tour,
                nuove_attrazioni_usate
            )

            pacchetto_parziale.pop()

        # Passo al prossimo indice mantenendo lo stato invariato
        self._ricorsione(
            start_index + 1,
            pacchetto_parziale,
            durata_corrente,
            costo_corrente,
            valore_corrente,
            attrazioni_usate
        )