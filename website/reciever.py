from website.command import get_commands_dict
from .constants import *
from .exceptions import *
from .services import *


# Reciever
class RecieverUseCases:

    # TODO get from user all his QUERIES
    def get_user_queries_history(self, attributes):
        if USER_ID not in attributes:
            return empty_field_exception(f"{ATTRIBUTES} is missing {USER_ID}")

        try:
            user = get_instance_from_db(attributes[USER_ID])

        except Exception as e:
            return bad_request_exception(f"get_user_queries_history(self, attributes) caught an exception fetching user: {e}")

        if user is None:
            result = f"Could not find a user with this id: {attributes[USER_ID]}"
        else:
            result = user

        return make_response({RESULT: result})


    def get_all_use_cases(self, attributes):
        use_cases_names = [key for key in get_commands_dict().keys()]
        return make_response({
            "useCases": use_cases_names
        })