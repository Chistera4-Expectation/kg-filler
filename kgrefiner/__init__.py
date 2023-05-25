import typing
from owlready2 import owlready, destroy_entity
from kgfiller import Commitable, Commit, logger
from kgfiller.kg import PATH_ONTOLOGY, KnowledgeGraph
from kgfiller.utils import first_or_none


def get_conflicting_classes(kg: KnowledgeGraph) -> typing.List[typing.Tuple[owlready.ThingClass, owlready.ThingClass]]:
    conflicting_classes = []
    for cls1 in kg.visit_classes_depth_first():
        conflict = first_or_none(cls1.conflict)
        if conflict:
            cls2 = first_or_none([cls for cls in kg.visit_classes_depth_first() if cls.name == conflict])
            if cls2:
                conflicting_classes.append((cls1, cls2))
    return conflicting_classes


def exclusive_classes_check(cls1: owlready.ThingClass, cls2: owlready.ThingClass) -> Commitable:
    message = "update the ontology"
    description = ""
    should_commit = False
    for individual in cls1.instances():
        classes = set(individual.is_a)
        if cls2 in classes:
            # Print the potential conflict to the user and wait for its decision
            logger.info(f"Individual {individual.name} is both a {cls1.name} and a {cls2.name}.")
            logger.info(f"Which one should it be?")
            logger.info(f"1. {cls1.name}")
            logger.info(f"2. {cls2.name}")
            logger.info(f"3. None of the above")
            logger.info(f"4. Skip this individual")
            while True:
                answer = input("Please enter your choice: ")
                if answer == "1":
                    description += f"Remove {individual.name} from {cls2.name}\n"
                    should_commit = True
                    individual.is_instance_of.remove(cls2)
                    break
                elif answer == "2":
                    description += f"Remove {individual.name} as {cls1.name}\n"
                    should_commit = True
                    individual.is_instance_of.remove(cls1)
                    break
                elif answer == "3":
                    description += f"Remove {individual.name} from {cls1.name} and {cls2.name}\n"
                    should_commit = True
                    individual.is_instance_of.remove(cls1)
                    individual.is_instance_of.remove(cls2)
                    break
                elif answer == "4":
                    break
    return Commit(message, [PATH_ONTOLOGY], description, should_commit)
