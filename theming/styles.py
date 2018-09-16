main_window_style = \
    """
    QMainWindow {
        background-color: @mainWindowBackground@;
    }
    
    QMainWindow::separator {
        background: @mainWindowBackground@;
    }
    
    QMenuBar {
        background-color: @mainWindowBackground@;
    }
    
    QWidget {
        background-color: @mainWindowBackground@;
    }
    """

settings_window_style = main_window_style

settings_categories_list_style = \
    """
        background-color: @settingsCategoriesListBackground@;
        color: @settingsCategoryText@
    """

settings_category_opened_style = \
    """
    QWidget {
        background-color: @settingsOpenedBackground@;
    }
    """

button_style = \
    """
    QPushButton {
        border: 2px solid @buttonBorder@;
        border-radius: 3px;
        background-color: @buttonBackground@;
        color: @buttonText@;
        width: 50px;
        height: 30px;
        padding: 0px 5px;
    }
    QPushButton:pressed {
        background-color: @buttonBackgroundPressed@;
    }
    """

nickname_label = \
    """
    QLabel {
        color: @nicknameTextColorDefault@;
        font-weight: bold;
        background-color: #00000000;
    }
    """

my_message_balloon = \
    """
    QWidget {
        color: @messageText@;
        background-color: @messageMyBackground@;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        border-bottom-left-radius: @blRadius@;
        border-bottom-right-radius: @brRadius@;
        padding: 5px;
    }
    """

their_message_balloon = \
    """
    QWidget {
        color: @messageText@;
        background-color: @messageTheirBackground@;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        border-bottom-left-radius: @blRadius@;
        border-bottom-right-radius: @brRadius@;
        padding: 5px;
    }
    """

service_message_balloon = \
    """
    QWidget {
        color: @messageServiceText@;
        background-color: @messageServiceBackground@;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        border-bottom-left-radius: @blRadius@;
        border-bottom-right-radius: @brRadius@;
        padding: 5px;
    }
    """

messages_list = \
    """
    QListWidget {
        background-color: @messagesListBackground@;
    }
    """

side_list_style = \
    """
    QListWidget {
        background-color: @sideListBackground@;
        color: @sideListText@;
    }
    """

multiline_input_style = \
    """
    QTextEdit {
        background-color: @multilineBackground@;
        color: @multilineTextColor@;
    }
    """

tabs_style = \
    """
    QTabBar::tab {
        padding: 5px;
        border-top-left-radius: 5px;
        border-top-right-radius: 5px;
    }
    
    QTabBar::tab:selected {
        background-color: @tabsSelectedTabBackground@;
        border-top: 1px solid @tabsSelectedTabBorder@;
        border-left: 1px solid @tabsSelectedTabBorder@;
        border-right: 1px solid @tabsSelectedTabBorder@;
    }
    
    QTabBar::tab:!selected {
        background-color: @tabsUnselectedTabBackground@;
    }
    
    QTabWidget::pane {
        background-color: #f00;
        border: none;
    }
    """
