from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.optimizers import Adam

from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from numpy.linalg import inv
from Dataset import *


class OptInterpolation:
    def __init__(self, observations, simulations, idx):
        self.scaler = StandardScaler()
        self.sim = self.scaler.fit_transform(simulations)
        self.obs = self.scaler.transform(observations)
        self.idx = idx
        self.C = np.identity(1)
        self.R = self.covariance_matrix(self.obs.T - np.dot(self.C, self.sim.T))  # covariance_matrix(self.obs.T)
        self.P = self.covariance_matrix(np.array(self.sim).T)
        self.range = range(len(self.obs))

    def kalman_gain(self, P, C, R):
        tempInv = inv(R + np.dot(C, np.dot(P, C.transpose())))
        res = np.dot(P, np.dot(C.transpose(), tempInv))
        return res

    def update_prediction(self, x, K, C, y):
        np.dot(C, x)
        np.dot(K, (y - np.dot(C, x)))
        res = x + np.dot(K, (y - np.dot(C, x)))
        return res

    def covariance_matrix(self, X):
        means = np.array([np.mean(X, axis=1)]).transpose()
        # print(means)
        dev_matrix = X - means
        # print(dev_matrix)
        #     print(X.shape)
        res = np.dot(dev_matrix, dev_matrix.transpose())  # /(X.shape[1]-1)
        return res

    def assimilate(self, R=None, plot=False, plot_length=120,
                   labels=['Optimal interpolation', 'Observations', 'AMS-MINNI modelled']):
        if R is None:
            R = self.covariance_matrix(self.obs.T - np.dot(self.C, self.sim.T))
        # K = self.kalman_gain(self.P, self.C, R)
        # self.updated = [self.update_prediction(self.sim[i], self.kalman_gain(self.P, self.C, R), self.C, self.obs[i]) for i in self.range]
        self.updated = []
        for i in self.range:  # self.range:
            self.updated.append(
                self.update_prediction(self.sim[i], self.kalman_gain(self.P, self.C, R), self.C, self.obs[i]))
        if plot:
            self.plot(plot_length, labels=labels)
            self.updated = self.scaler.inverse_transform(self.updated)

        return self.updated

    def plot(self, plot_length, labels):
        updated = self.scaler.inverse_transform(self.updated)
        obs = self.scaler.inverse_transform(self.obs)
        sim = self.scaler.inverse_transform(self.sim)
        plt.plot(pd.DataFrame(updated, index=self.idx)[:plot_length], 'b--', label=labels[0])
        plt.plot(pd.DataFrame(obs, index=self.idx)[:plot_length], 'r-', label=labels[1])
        plt.plot(pd.DataFrame(sim, index=self.idx)[:plot_length], 'g-', label=labels[2])
        plt.plot()
        plt.legend()
        plt.rcParams["figure.figsize"] = (18, 10)
        plt.show()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    location = 'C:\\Users\\Nikodemas\\Desktop\\IMPERIAL material\\MAGIS\\duomenys\\NO2_data_final.dat'
    df1 = pd.read_csv(location)
    df = df1.copy()
    df_brun = df[df['sta_name'] == 'BR1_Brunico']
    df_brun.sort_values(by=['date'])
    # # df_brun.loc[:, 'date'] = pd.to_datetime(df_brun.loc[:, 'date'], format='%Y-%m-%d %H:%M')
    # # df_brun = df_brun.replace(-999.0000, np.nan)
    # # df_brun['day_date'] = pd.to_datetime(df_brun['date']).dt.date
    # # df_brun['obs'] = df_brun['obs'].fillna(df_brun.groupby('day_date')['obs'].transform('median'))
    # # df_brun['sim'] = df_brun['sim'].fillna(df_brun.groupby('day_date')['sim'].transform('median'))
    # # while df_brun['obs'].isna().sum():
    # #     df_brun['obs'] = df_brun['obs'].fillna(df_brun['obs'].shift(24))
    # # while df_brun['sim'].isna().sum():
    # #     df_brun['sim'] = df_brun['sim'].fillna(df_brun['sim'].shift(24))
    # # df_brun = df_brun.set_index('date')
    # scaler = StandardScaler()  # MinMaxScaler(feature_range=(-1, 1))
    # dataset = Dataset(df_brun, 8736, 48, 48, ['sim', 'day_sin', 'day_cos'], ['sim'], 12, 24, scaler, scaler, scaled_cols_oth=None)
    #
    # model = Sequential()
    # model.add(LSTM(50, return_sequences=True, input_shape=(None, 3)))
    # model.add(LSTM(35, return_sequences=False))
    # model.add(Dense(1))
    #
    #
    # regressor = Regressor(dataset, model)
    # regressor.fit(2)
    # preds, base_loss, model_loss = regressor.predict()
    # print(f"Baseline loss: {base_loss}")
    # print(f"Model loss: {model_loss}")

    df_brun = clean_na(df_brun, ['sim', 'obs'], 'median', -999.0000)
    df_brun = add_day_trig(df_brun)
    df_brun = add_month_trig(df_brun)

    scaler = StandardScaler()  # MinMaxScaler(feature_range=(-1, 1))
    dataset = Dataset(df_brun, 52608, 8760, 8760, ['sim', 'day_sin', 'day_cos', 'month_sin', 'month_cos'],
                      ['sim', 'obs'],
                      19, 24)  # , scaler, scaler)

    data_ass = OptInterpolation(dataset.train_data_out.iloc[:1200][['obs']].values,
                                dataset.train_data_out.iloc[:1200][['sim']].values,
                                dataset.train_data_out.iloc[:1200][['obs']].index)
    updates = data_ass.assimilate(plot=True)
    # model = Sequential()
    # model.add(LSTM(40, return_sequences=True, input_shape=(None, 5)))
    # model.add(LSTM(45, return_sequences=False))
    # model.add(Dense(1))
    #
    # regressor = Regressor(dataset, model)
    # regressor.fit(20)
    # regressor.predict()

    # import pickle
    #
    # filename = 'finalized_model.sav'
    # pickle.dump(model, open(filename, 'wb'))
    # # preds, base_loss, model_loss = regressor.predict()
    # # print(f"Baseline loss: {base_loss}")
    # # print(f"Model loss: {model_loss}")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/