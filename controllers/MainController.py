class MainController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # connecte les signaux de la vue aux méthodes du contrôleur
        # ça servira à faire communiquer les actions de l'utilisateur (clics sur les boutons) avec les modifications du modèle et la mise à jour de la vue
        self._connect_signals()

    def _connect_signals(self):
        self.view.btn_increment.clicked.connect(self.handle_increment)  # si on reçoit le signal "clicked" du bouton d'incrémentation, on appelle la méthode handle_increment
        self.view.btn_reset.clicked.connect(self.handle_reset)  # si on reçoit le signal "clicked" du bouton de réinitialisation, on appelle la méthode handle_reset

    def handle_increment(self):
        self.model.increment_counter()  # on demande D'ABORD au modèle d'incrémenter le compteur
        self.view.update_counter_display(self.model.counter)  # puis on met à jour l'affichage de la vue avec la nouvelle valeur du compteur (qu'on récupère du modèle)

    def handle_reset(self):
        # même principe ici que pour l'incrémentation
        self.model.reset_counter()
        self.view.update_counter_display(self.model.counter)
