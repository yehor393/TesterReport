

def set_tabs_for_model(self, model):
    """Додає потрібні вкладки залежно від моделі."""
    self.clear_tabs()  # Спочатку видаляємо всі вкладки

    if model == "FX6":
        self.tab_widget.addTab(self.outside_steam, "Outside")
        self.tab_widget.addTab(self.value, "Value")
        self.tab_widget.addTab(self.final, "Final")
    elif model == "CX1":
        self.tab_widget.addTab(self.outside_convector, "Outside")
        self.tab_widget.addTab(self.value, "Value")
        self.tab_widget.addTab(self.final, "Final")