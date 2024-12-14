import pandas as pd
from PyQt6.QtCore import QAbstractTableModel, Qt
from PyQt6.QtGui import QColor

class PandasModel(QAbstractTableModel):
    def __init__(self, df, highlighted_rows=None):
        super().__init__()
        self._df = df
        self.highlighted_rows = highlighted_rows or []

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parent=None):
        return self._df.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        row, col = index.row(), index.column()

        # Formato de fondo para filas resaltadas
        if role == Qt.ItemDataRole.BackgroundRole and row in self.highlighted_rows:
            return QColor("#ffff99")  # Fondo amarillo claro

        # Formato de texto para filas resaltadas
        if role == Qt.ItemDataRole.ForegroundRole and row in self.highlighted_rows:
            return QColor("#ff0000")  # Texto rojo

        # Valores de la celda
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            value = self._df.iloc[row, col]
            return str(value) if not pd.isna(value) else ""

        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if index.isValid() and role == Qt.ItemDataRole.EditRole:
            try:
                dtype = self._df.iloc[:, index.column()].dtype
                if pd.api.types.is_numeric_dtype(dtype):
                    value = float(value)
                self._df.iat[index.row(), index.column()] = value
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole])
                return True
            except ValueError:
                print("Error: El valor ingresado no es válido para esta columna.")
                return False
        return False

    def flags(self, index):
        if index.isValid():
            return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
        return Qt.ItemFlag.NoItemFlags

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._df.columns[section])
            if orientation == Qt.Orientation.Vertical:
                return str(self._df.index[section])
        return None

    def add_empty_row(self):
        empty_row = pd.Series([None] * self._df.shape[1], index=self._df.columns)
        self._df = pd.concat([self._df, pd.DataFrame([empty_row])], ignore_index=True)
        self.layoutChanged.emit()

    def get_dataframe(self):
        return self._df