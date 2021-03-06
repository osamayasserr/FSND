import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    ENV = 'development'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DB_URL') or \
        f"postgresql://postgres:{os.environ.get('DB_PASS')}@localhost:5432/fyyur"


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DB_URL') or \
        'sqlite:///' + os.path.join(basedir, 'test_db.sqlite')


config = {
    'development': DevConfig,
    'testing': TestConfig,
    'default': DevConfig
}
