from typing import Dict, List
from pydantic import BaseModel


class BaseClass(object):
    def __init__(self, classtype):
        self._type = classtype


def ClassFactory(name: str, attribute: str, validator: str, BaseClass=BaseModel) -> object:
    """
    This function makes dynamic classes from scratch, by changing python metaclass behaviors,
    :param name: will be the name of constructed class or model
    :param arguments: class variables implemented by custom attribute microservice
    :param BaseClass: constructor uses BaseClass as main behaviour for create class through type
    :return:
    """

    def __init__(self, **kwargs: List[str]):
        for key, value in kwargs.items():

            if key not in attribute:
                raise TypeError("Argument %s not valid for %s"
                                % (key, self.__class__.__name__))

            setattr(self, key, value)  # class attributes will be registered here

        BaseClass.__init__(self, name[:-len("Class")])  # initializing first class method

    new_class = type(name, (BaseModel,), {attribute: validator})  # creating class
    return new_class


SpecialClass = ClassFactory("DoctorMeisamBoos", "etgdfgh", "dfhdfh")
s = SpecialClass()
print(type(SpecialClass))
print(type(s))
print(vars(SpecialClass))
