# run.py
import os
import time
from app.app import app, initialize_database
from app.extensions import logger


def main():
    """Initialise la base de données et lance l'application Flask."""
    # Initialisation de la base dans le contexte de l'application
    with app.app_context():
        initialize_database()

    # Paramètres d'exécution
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    debug = app.config.get("DEBUG", False)

    try:
        app.run(host=host, port=port, debug=debug, use_reloader=debug)
    except OSError as e:
        if getattr(e, "winerror", None) == 10038:
            logger.error("Erreur de socket Windows. Tentative de redémarrage du serveur...")
            time.sleep(1)
            app.run(host=host, port=port, debug=debug, use_reloader=debug)
        else:
            logger.error(f"Erreur de socket non gérée : {e}")
            raise

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        logger.critical("Arrêt du programme suite à une erreur d'initialisation")
        raise
    except Exception as exc:
        logger.critical(f"Erreur inattendue : {exc}")
        raise SystemExit(1)