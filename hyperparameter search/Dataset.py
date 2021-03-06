from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.optimizers import Adam

from sklearn.preprocessing import StandardScaler, MinMaxScaler
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from utils import *

"""
Class responsible for the convenient data unit creation,
cleanup and split so that it could be used by the ML models
"""


class IdScaler:
    """
    Dummy class if data doesn't need to be scaled
    """

    def fit_transform(self, x):
        return x

    def transform(self, x):
        return x

    def inverse_transform(self, x):
        return x


class Dataset:
    def __init__(self, df, train_size=52608, val_size=8760, test_size=8760,
                 input_col=['sim', 'day_sin', 'day_cos', 'month_sin', 'month_cos'], label_col=['sim'], n_input=1,
                 batch_size=24, x_scaler=StandardScaler(), y_scaler=StandardScaler(), scaled_col_base=['sim'],
                 scaled_cols_oth=['obs'], base_pred=False):
        """
        :param df: panda df to be processed
        :param train_size: training set size
        :param val_size: validation set size
        :param test_size: test set size
        :param input_col: columns used for input
        :param label_col: label/output column
        :param n_input: input sequence length
        :param x_scaler: input feature scaler
        :param y_scaler: output feature scaler
        :param scaled_col_base: main feature for scaling (for DNA)
        :param scaled_cols_oth: secondary features scaled with the params of the main feature (for DNA)
        :param base_pred: naive forecasting values
        """
        self.x_scaler = x_scaler
        self.y_scaler = y_scaler
        self.train_size = train_size
        self.val_size = val_size
        self.test_size = test_size
        self.n_input = n_input

        self.train_data_in = df[input_col].iloc[:train_size]
        self.val_data_in = df[input_col].iloc[train_size - n_input:train_size + val_size]
        self.test_data_in = df[input_col].iloc[train_size + val_size - n_input:train_size + val_size + test_size]
        self.test_idx = df[input_col].iloc[train_size + val_size:train_size + val_size + test_size].index
        if base_pred:
            self.base_preds = df[label_col].iloc[train_size + val_size - 1:train_size + val_size + test_size - 1].values

        self.train_data_out = df[label_col].iloc[:train_size]
        self.val_data_out = df[label_col].iloc[train_size - n_input:train_size + val_size]
        self.test_data_out = df[label_col].iloc[train_size + val_size - n_input:train_size + val_size + test_size]

        self.train_data_in[scaled_col_base], self.train_data_out[scaled_col_base] = self.x_scale(
            self.train_data_in[scaled_col_base]), self.y_scale(self.train_data_out[scaled_col_base])
        self.val_data_in[scaled_col_base], self.val_data_out[scaled_col_base] = self.x_scale(
            self.val_data_in[scaled_col_base], False), self.y_scale(self.val_data_out[scaled_col_base], False)
        self.test_data_in[scaled_col_base], self.test_data_out[scaled_col_base] = self.x_scale(
            self.test_data_in[scaled_col_base], False), self.y_scale(self.test_data_out[scaled_col_base], False)

        if base_pred:
            self.base_preds = self.y_scale(self.base_preds, False)

        if scaled_cols_oth is not None:
            for col in scaled_cols_oth:
                self.train_data_in[[col]] = self.x_scale(self.train_data_in[[col]], False)
                self.val_data_in[[col]] = self.x_scale(self.val_data_in[[col]], False)
                self.test_data_in[[col]] = self.x_scale(self.test_data_in[[col]], False)
                self.train_data_out[[col]] = self.y_scale(self.train_data_out[[col]], False)
                self.val_data_out[[col]] = self.y_scale(self.val_data_out[[col]], False)
                self.test_data_out[[col]] = self.y_scale(self.test_data_out[[col]], False)

        self.train_gen = TimeseriesGenerator(self.train_data_in.values, self.train_data_out.values, n_input,
                                             batch_size=batch_size)
        self.val_gen = TimeseriesGenerator(self.val_data_in.values, self.val_data_out.values, n_input,
                                           batch_size=batch_size)
        self.test_gen = TimeseriesGenerator(self.test_data_in.values, self.test_data_out.values, n_input,
                                            batch_size=len(self.test_data_in.values))

    def x_scale(self, x, training=True):
        """
        Method that scales input features
        :param x: values to be scaled
        :return: scaled values
        """
        if training:
            return self.x_scaler.fit_transform(x)
        return self.x_scaler.transform(x)

    def y_scale(self, y, training=True):
        """
        Method that scales output features
        :param y: values to be scaled
        :return: scaled values
        """
        if training:
            return self.y_scaler.fit_transform(y)
        return self.y_scaler.transform(y)
