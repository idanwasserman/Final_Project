from abc import ABCMeta, abstractstaticmethod
import sys, inspect
  

# ICommand interface
class ICommand(metaclass=ABCMeta):

    @abstractstaticmethod
    def execute():
        """A static interface method"""


############################################################

# START each USE CASE CLASS with the prefix 'UseCase'
# for example: 'UseCase1', 'UseCase2', 'UseCaseDoSomething'

############################################################
class UseCase_GetUserQueriesHistory(ICommand):
    def __init__(self, use_case):
        self._use_case = use_case

    def execute(self, attributes):
        return self._use_case.get_user_queries_history(attributes)


class UseCase_GetAllUseCases(ICommand):
    def __init__(self, use_case):
        self._use_case = use_case

    def execute(self, attributes):
        return self._use_case.get_all_use_cases(attributes)


def get_commands_dict():
    from .reciever import RecieverUseCases

    commands_dict = {}
    reciever = RecieverUseCases()
    cls_members = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    cls_names = [name for (name, c) in cls_members]
    use_cases_names = [name for name in cls_names if name.startswith("UseCase")]
    for name in use_cases_names:
        cls = globals()[name]
        commands_dict[name] = cls(reciever)
    return commands_dict
