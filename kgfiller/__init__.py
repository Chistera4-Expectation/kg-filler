import logging
import pathlib


logger = logging.getLogger("kgfiller")
logger.setLevel(logging.DEBUG)


PATH_DATA_DIR = pathlib.Path(__file__).parent.parent / "data"
logger.debug("PATH_DATA_DIR = %s", PATH_DATA_DIR.absolute())

ONTOLOGY_PATH = PATH_DATA_DIR / "ontology.owl"
logger.debug("ONTOLOGY_PATH = %s", ONTOLOGY_PATH.absolute())


if not ONTOLOGY_PATH.exists():
    raise FileNotFoundError(f"ONTOLOGY_PATH {ONTOLOGY_PATH.absolute()} does not exist")
