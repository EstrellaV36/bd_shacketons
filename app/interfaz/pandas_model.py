import pandas as pd
from PyQt6.QtCore import QAbstractTableModel, Qt

class PandasModel(QAbstractTableModel):
    def __init__(self, df):
        super().__init__()
        self._df = df

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parent=None):
        return self._df.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                return str(self._df.iloc[index.row(), index.column()]) if not pd.isna(self._df.iloc[index.row(), index.column()]) else ""
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if index.isValid() and role == Qt.ItemDataRole.EditRole:
            try:
                dtype = self._df.iloc[:, index.column()].dtype
                if pd.api.types.is_numeric_dtype(dtype):
                    value = float(value)
                self._df.iat[index.row(), index.column()] = value
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
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
                return self._df.columns[section]
            if orientation == Qt.Orientation.Vertical:
                return str(self._df.index[section])
    
    def add_empty_row(self):
        empty_row = pd.Series([None] * self._df.shape[1], index=self._df.columns)
        self._df = pd.concat([self._df, pd.DataFrame([empty_row])], ignore_index=True)
        self.layoutChanged.emit()

    def get_dataframe(self):
        return self._df
