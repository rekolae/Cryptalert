"""
Main entry point for the application

Emil Rekola <emil.rekola@hotmail.com>
"""

from cryptalert.app import Application


def start_application():
    """
    Start the cryptalert application
    """

    app = Application()
    app.run()


if __name__ == '__main__':
    start_application()
