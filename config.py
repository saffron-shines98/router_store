from app.connections import SqlConnection, RedisConnection, RabbitMQConnection, SqlConnectionpooling, SqlConnectionNodeSso, SqlConnectionpoolingnodeapp


class Config:

    ES_CONN = None
    ENV = 2
    if ENV == 1:
        MYSQL_CONFIG = {
            'host': '127.0.0.1',
            'user': 'poqfcwgwub',
            'passwd': 'npW9U36Qd6SsT4hl',
            'db': 'nzkrqvrxme',
            'charset': 'utf8',
            'port': 3308
        }
    else:
        MYSQL_CONFIG = {
            'host': 'az-cvstagedb.craftsvilla.com',
            'user': 'stage-db-user',
            'passwd': 'vbG985VnWRj7YL3',
            'db': 'stagingdb01'
        }

    if ENV == 1:
        REDIS_CONFIG ={
            'host': '127.0.0.1',
            'port': 6379,
            'password': '3uHWdWn951enc6oX51wptTf92EgQwvmgIAzCaBQTEKU='
        }
        # REDIS_CONFIG ={
        #     'host': '127.0.0.1',
        #     'port': 6479,
        #     'password': '3uHWdWn951enc6oX51wptTf92EgQwvmgIAzCaBQTEKU='
        # }
    else:
        REDIS_CONFIG ={
            'host': '127.0.0.1',
            'port': 6379
        }
    REDIS_CONN = RedisConnection.get_redis_connections(REDIS_CONFIG)
    MYSQL_CONN_POOLING = SqlConnectionpooling(MYSQL_CONFIG)
    MYSQL_CONN = SqlConnection(MYSQL_CONFIG)
    API_ACCESS_KEY = '11uhgfdfhgn!@fdDFDFv!@#$asfdsvcF'
    VERSIONS_ALLOWED = ['1']
    SSO_COORDINATOR_URI ="http://auth.plotch.io"
    # SSO_COORDINATOR_URI = "http://127.0.0.1:5000"
    Authorization ='11uhgfdfhgn!@fdDFDFv!@#$asfdsvcF'
    # RABBITMQ_CREDENTIALS = {
    #     'HOST': 'dev-rabbit.plotch.ai',
    #     'USER': 'cvuser',
    #     'PASSWORD': 'cv@user*',
    #     'PORT': '5672'
    # }
    RABBITMQ_CREDENTIALS = {
        'HOST': 'dev-rabbit-uat.plotch.ai',
        'USER': 'cvuser',
        'PASSWORD': 'cv@user*',
        'PORT': '5672',
        "RABBIT_HEARTBEAT": 5
    }

    # RABBITMQ_CREDENTIALS = {
    #     'HOST': 'rabbit.plotch.ai',
    #     'USER': 'remotecv',
    #     'PASSWORD': '28LrnMR%K|8%MR58',
    #     'PORT': '5672'
    # }
    RABBITMQ = {
        'CLOUDAMQP_URL': "amqp://{0}:{1}@{2}:{3}/".format(
            RABBITMQ_CREDENTIALS.get('USER'),
            RABBITMQ_CREDENTIALS.get('PASSWORD'),
            RABBITMQ_CREDENTIALS.get('HOST'),
            RABBITMQ_CREDENTIALS.get('PORT'))
    }
    RABBITMQ_CONNECTION = RabbitMQConnection(RABBITMQ.get('CLOUDAMQP_URL'))
    # MYSQL_CONN_NODE_SSO_CREDIANTIAL = {
    #     'host': '127.0.0.1',
    #     'user': 'read-vijendra',
    #     'passwd': 'Zutpzg6QHSZ7aVjj1',
    #     'db': 'nodesso',
    #     'port': 3308
    # }
    MYSQL_CONN_NODE_SSO_CREDIANTIAL = {
        'host': 'az-cvstagedb.craftsvilla.com',
        'user': 'stage-db-user',
        'passwd': 'vbG985VnWRj7YL3',
        'db': 'stagingdb01'
    }
    MYSQL_CONN_NODE_SSO = SqlConnectionNodeSso(MYSQL_CONN_NODE_SSO_CREDIANTIAL)

    MYSQL_NODEAPP = {
        'host': 'az-cvstagedb.craftsvilla.com',
        'user': 'stage-db-user',
        'passwd': 'vbG985VnWRj7YL3',
        'db': 'stagingdb01'
    }
    MYSQL_CONN_NODEAPP = SqlConnectionpoolingnodeapp(MYSQL_NODEAPP)


