import owlready2 as owlready
from kgfiller import logger, PATH_DATA_DIR
from lazy_property import LazyProperty
import pathlib
import typing


ONTOLOGY_PATH = PATH_DATA_DIR / "ontology.owl"
logger.debug("ONTOLOGY_PATH = %s", ONTOLOGY_PATH.absolute())


if not ONTOLOGY_PATH.exists():
    raise FileNotFoundError(f"ONTOLOGY_PATH {ONTOLOGY_PATH.absolute()} does not exist")


class KnowledgeGraph:
    def __init__(self, path: pathlib.Path=ONTOLOGY_PATH) -> None:
        self._path = path
        self._uri = path.as_uri()
    
    @LazyProperty
    def onto(self) -> owlready.Ontology:
        logger.debug("Loading ontology from %s", self._uri)
        return owlready.get_ontology(self._uri).load()
    
    def _find_root_class(self):
        things = set()
        for cls in self.onto.classes():
            if cls.ancestors() == {owlready.Thing, cls}:
                things.add(cls)
        if len(things) == 1:
            return next(iter(things))
        else:
            return owlready.Thing
    
    def add_instance(self, cls: str | owlready.ThingClass, name: str, add_to_class_if_existing: bool=True) -> owlready.Thing:
        cls = self.onto[cls] if isinstance(cls, str) else cls
        if name in cls.instances():
            instance = self.onto[cls]
            if add_to_class_if_existing:
                if instance.is_a(cls):
                    logger.debug("Do nothing: entity %s is already instance of class %s", instance, cls)
                else:
                    cls.is_instance_of.append(instance)
                    logger.debug("Added instance %s to class %s", instance, cls)
            else:
                raise KeyError(f"Instance {name} already exists in classes {instance.is_instance_of}")
        else:
            instance = cls(name)
            logger.debug("Created instance %s of class %s", instance, cls)
        return instance

    def visit_classes_depth_first(self, root: str | owlready.ThingClass | None = None, postorder=True) -> typing.Iterable[owlready.ThingClass]:
        root = self._find_root_class() if root is None else root
        root = self.onto[root] if isinstance(root, str) else root
        if not postorder:
            yield root
        for child in root.subclasses():
            yield from self.visit_classes_depth_first(child, postorder)
        if postorder:
            yield root

    def __enter__(self) -> "KnowledgeGraph":
        self.onto
        return self
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.onto.save(str(self._path))
