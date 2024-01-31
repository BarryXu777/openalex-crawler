from enum import Enum


class ItemEnum(Enum):
    work = (1, 'paper')
    author = (2, 'scholar')
    source = (3, 'venue')
    institution = (4, 'org')
    concept = (5, 'concept')

    def __init__(self, value, es_name: str):
        self._value_ = value
        self.es_name = es_name

    def __str__(self):
        return self.name
