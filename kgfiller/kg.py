import pathlib
import typing

import owlready2 as owlready
import unidecode
from lazy_property import LazyProperty

from kgfiller import logger, PATH_DATA_DIR, replace_symbols_with
from kgfiller.utils import *

PATH_ONTOLOGY = PATH_DATA_DIR / "ontology.owl"
logger.debug("ONTOLOGY_PATH = %s", PATH_ONTOLOGY.absolute())

if not PATH_ONTOLOGY.exists():
    raise FileNotFoundError(f"ONTOLOGY_PATH {PATH_ONTOLOGY.absolute()} does not exist")


def is_leaf(cls: owlready.ThingClass) -> bool:
    return len(cls.descendants(include_self=False)) == 0


def subtype(cls1: owlready.ThingClass, cls2: owlready.ThingClass, strict: bool = False) -> bool:
    return overlap([cls1], cls2.descendants(include_self=not strict))


def supertype(cls1: owlready.ThingClass, cls2: owlready.ThingClass, strict: bool = False) -> bool:
    return overlap([cls1], cls2.ancestors(include_self=not strict))


def instance_of(instance: owlready.Thing, cls: owlready.ThingClass) -> bool:
    return overlap(instance.is_a, cls.descendants())


def human_name(cls_or_instance: owlready.ThingClass | owlready.Thing) -> str:
    return first_or_none(cls_or_instance.fancyName) or cls_or_instance.name


def owl_name(name: str, instance: bool = True) -> str:
    name = unidecode.unidecode(name)
    name = name.strip()
    name = replace_symbols_with(name, "_")
    name = name.lower()
    if not instance:
        name = name.capitalize()
    return name


class KnowledgeGraph:
    def __init__(self, path: pathlib.Path = PATH_ONTOLOGY) -> None:
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

    def add_property(self, cls_or_instance: owlready.ThingClass | owlready.Thing,
                     property: str | owlready.ObjectPropertyClass,
                     value: owlready.ThingClass | owlready.Thing | str) -> None:
        if isinstance(property, owlready.ObjectPropertyClass):
            property = property.name
        property_values = getattr(cls_or_instance, property)
        if value not in property_values:
            property_values.append(value)
        logger.debug("Set property '%s' of %s to %s", property, cls_or_instance, value)

    def set_class_of_instance(self, instance: owlready.Thing, cls: str | owlready.ThingClass) -> owlready.Thing:
        if instance_of(instance, cls):
            for c in instance.is_instance_of:
                if c != owlready.Thing and supertype(c, cls, strict=True):
                    instance.is_instance_of.remove(c)
                    instance.is_instance_of.append(cls)
                    logger.debug("Move instance %s to class %s from more specific class %s", instance, cls, c)
                else:
                    logger.debug(
                        "Do nothing: entity %s is already instance of classes %s, "
                        "therefore it is already an instance of %s",
                        instance, instance.is_a, cls)
        else:
            instance.is_instance_of.append(cls)
            logger.debug("Added instance %s to class %s", instance, cls)
        return instance

    def add_instance(self, cls: str | owlready.ThingClass, name: str,
                     add_to_class_if_existing: bool = True) -> owlready.Thing:
        fancy_name = name
        name = owl_name(name)
        cls = self.onto[cls] if isinstance(cls, str) else cls
        instance = first_or_none(filter(lambda i: i.name == name, cls.instances()))
        if instance is not None:
            if add_to_class_if_existing:
                self.set_class_of_instance(instance, cls)
            else:
                raise KeyError(f"Instance {name} already exists in classes {instance.is_instance_of}")
        else:
            instance = cls(name)
            logger.debug("Created instance %s of class %s", instance, cls)
        if self.onto.fancyName is not None and name != fancy_name:
            self.add_property(instance, "fancyName", fancy_name)
        return instance

    def visit_classes_depth_first(self, root: str | owlready.ThingClass | None = None, postorder=True) -> \
            typing.Iterable[owlready.ThingClass]:
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
