import os
from pygqlc import GraphQLClient


def setup_gql():
    __environments = ["prod", "dev"]
    gql = GraphQLClient()

    # * API test.app environment
    gql.addEnvironment(
        name='dev',
        url=os.environ.get('API_DEV'),
        wss=os.environ.get('WSS_DEV'),
        headers={'Authorization': os.environ.get('TOKEN_DEV')})

    # * API prod.app environment
    gql.addEnvironment(
        name='prod',
        url=os.environ.get('API'),
        wss=os.environ.get('WSS'),
        headers={'Authorization': os.environ.get('TOKEN')})

    env = os.environ.get('ENV')
    if not env in __environments:
        raise EnvironmentError(
            f"Environment '{env}' is not available. Try one of the followings: {__environments}")
    # * Sets the environment selected in the .env file
    gql.setEnvironment(env)
    return gql
