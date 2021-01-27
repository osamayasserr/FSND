from . import main
from flask import render_template
from logging import Formatter, FileHandler


@main.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@main.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


# if not main.debug:
#     file_handler = FileHandler('error.log')
#     file_handler.setFormatter(
#         Formatter(
#             '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
#     )
#     log.setLevel(log.INFO)
#     file_handler.setLevel(log.INFO)
#     log.addHandler(file_handler)
#     log.info('errors')
