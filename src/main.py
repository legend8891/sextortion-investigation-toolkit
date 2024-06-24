from controllers.main_controller import MainController
from views.main_view import MainView


def main() -> None:
    """
    Create instance of mainview and controller and launch application
    :return:
    """
    main_view = MainView()
    main_controller = MainController(main_view)
    main_controller.run()


if __name__ == "__main__":
    main()
