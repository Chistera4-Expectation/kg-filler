import owlready2 as owlready
from kgfiller import logger, PATH_DATA_DIR, replace_symbols_with
from lazy_property import LazyProperty
import pathlib
import typing
import unidecode


PATH_ONTOLOGY = PATH_DATA_DIR / "ontology.owl"
logger.debug("ONTOLOGY_PATH = %s", PATH_ONTOLOGY.absolute())


if not PATH_ONTOLOGY.exists():
    raise FileNotFoundError(f"ONTOLOGY_PATH {PATH_ONTOLOGY.absolute()} does not exist")


def first(iterable: typing.Iterable[typing.Any]) -> typing.Any:
    return next(iter(iterable))


def first_or_none(iterable: typing.Iterable[typing.Any]) -> typing.Any:
    try:
        return first(iterable)
    except StopIteration:
        return None


def instance_of(instance: owlready.Thing, cls: owlready.ThingClass) -> bool:
    for type in cls.ancestors():
        for t in instance.is_a:
            if t == type:
                return True
    return False


def human_name(cls_or_instance: owlready.ThingClass | owlready.Thing) -> str:
    return first_or_none(cls_or_instance.fancyName) or cls_or_instance.name


def owl_name(name: str, instance: bool=True) -> str:
    name = unidecode.unidecode(name)
    name = name.strip()
    name = replace_symbols_with(name, "_")
    name = name.lower()
    if not instance:
        name = name.capitalize()
    return name


class KnowledgeGraph:
    def __init__(self, path: pathlib.Path=PATH_ONTOLOGY) -> None:
        self._path = path
        self._uri = path.as_uri()

    @property
    def path(self) -> pathlib.Path:
        return self._path
    
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
            return first(things)
        else:
            return owlready.Thing
        
    def add_property(self, cls_or_instance: owlready.ThingClass | owlready.Thing, property: str, value: owlready.ThingClass | owlready.Thing | str) -> None:
        property_values = getattr(cls_or_instance, property)
        if value not in property_values:
            property_values.append(value)
        logger.debug("Set property '%s' of %s to %s", property, cls_or_instance, value)
    
    def add_instance(self, cls: str | owlready.ThingClass, name: str, add_to_class_if_existing: bool=True) -> owlready.Thing:
        fancy_name = name
        name = owl_name(name)
        cls = self.onto[cls] if isinstance(cls, str) else cls
        instance = first_or_none(filter(lambda i: i.name == name, cls.instances()))
        if instance is not None:
            if add_to_class_if_existing:
                if instance_of(instance, cls):
                    logger.debug("Do nothing: entity %s is already instance of class %s", instance, cls)
                else:
                    instance.is_instance_of.append(cls)
                    logger.debug("Added instance %s to class %s", instance, cls)
            else:
                raise KeyError(f"Instance {name} already exists in classes {instance.is_instance_of}")
        else:
            instance = cls(name)
            logger.debug("Created instance %s of class %s", instance, cls)
        if self.onto.fancyName is not None and name != fancy_name:
            self.add_property(instance, "fancyName", fancy_name)
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

    def save(self) -> None:
        self.onto.save(str(self._path))

    def __enter__(self) -> "KnowledgeGraph":
        self.onto
        return self
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.save()


def create_query_for_instances(cls: owlready.ThingClass) -> str:
    cls_name = f'{human_name(cls)}'
    return [f'{it} {cls_name}' for it in { 
        "instances list for class",
        "examples list for",
    }]
