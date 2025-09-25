import os

WATCH_PATH = r"C:\Users\juankroos\PycharmProjects\AgentIA\Agent"
known_files = set(os.listdir(WATCH_PATH))


def check_new_files() -> list[str]:
    """
    Retourne les nouveaux fichiers detectes dans le dossier WATCH_PATH.
    """
    global known_files
    current_files = set(os.listdir(WATCH_PATH))
    new_files = list(current_files - known_files)
    known_files = current_files
    path = r"C:\Users\juankroos\PycharmProjects\AgentIA\Script\script_instruction.txt"
    return path

a = check_new_files()
print(a)


import os
import yaml
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, filename="agent_p.log")
logger = logging.getLogger(__name__)

# Charger la config YAML
def load_config(path="agent_config.yaml") -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("Fichier agent_config.yaml introuvable")
        raise SystemExit("Erreur : Fichier agent_config.yaml introuvable")
    except yaml.YAMLError as e:
        logger.error(f"Erreur dans le parsing YAML : {e}")
        raise SystemExit(f"Erreur : Format YAML invalide dans agent_config.yaml")

try:
    config = load_config()
    watch_path = config["agent_p"]["watch_path"]  # Ex. : "C:\\Users\\juankroos\\PycharmProjects\\AgentIA\\Script"
    instruction_file = config["agent_p"]["instruction_file"]  # Ex. : "script_instruction.txt"
except KeyError as e:
    logger.error(f"Erreur dans la config YAML : clé manquante {e}")
    raise SystemExit(f"Erreur : Clé manquante dans agent_config.yaml : {e}")

def read_instruction_file() -> str:
    """Lit le contenu du fichier d'instructions spécifié dans la config."""
    file_path = os.path.join(watch_path, instruction_file)
    try:
        if not os.path.exists(file_path):
            logger.error(f"Fichier {file_path} introuvable")
            raise FileNotFoundError(f"Erreur : Fichier {file_path} introuvable")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                logger.warning(f"Fichier {file_path} est vide")
                raise ValueError(f"Erreur : Fichier {file_path} est vide")
            logger.info(f"Fichier {file_path} lu avec succès")
            return content
    except PermissionError:
        logger.error(f"Permission refusée pour lire {file_path}")
        raise SystemExit(f"Erreur : Permission refusée pour {file_path}")
    except Exception as e:
        logger.error(f"Erreur lors de la lecture de {file_path} : {e}")
        raise SystemExit(f"Erreur : Impossible de lire {file_path} : {e}")

# Test
if __name__ == "__main__":
    try:
        content = read_instruction_file()
        print(f"Contenu du fichier : {content[:100]}...")  # Affiche les 100 premiers caractères
    except Exception as e:
        print(f"Erreur : {e}")