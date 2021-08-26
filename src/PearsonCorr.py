import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

class PearsonCorr:
    def __init__(self, x, y):
        self.x = np.array(x)
        self.y = np.array(y)

    def correlation(self):
        self.pear_corr, _ = pearsonr(self.x, self.y)
        return self.pear_corr

    def plot_corr(self, labels, title, years=[2007, 2010, 2013]):
        fig, ax = plt.subplots()
        ax.scatter(self.x, self.y, color='r', s=600)

        m, b = np.polyfit(self.x, self.y, 1)

        plt.plot(self.x, m * self.x + b, linewidth=10)

        for i, txt in enumerate(years):
            ax.annotate(txt, (self.x[i], self.y[i]), fontsize=36)
        plt.xlabel(labels[0], fontdict={'size': 36})
        plt.ylabel(labels[1], fontdict={'size': 36})
        plt.xticks(fontsize=30)
        plt.yticks(fontsize=30)
        plt.title(title, {'fontsize': 40})
        plt.show()

if __name__ == '__main__':
    corr = PearsonCorr([24.13440428, 22.49934405, 30.81200657], [14500, 14128, 15607])
    print(f"Pearson's correlation: {corr.correlation():.3f}")
    corr.plot_corr()
