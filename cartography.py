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