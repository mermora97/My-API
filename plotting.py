import matplotlib.pyplot as plt
import numpy as np


def emojiAutolabel(ax,sentiments):
    emojies = {0:'😐',1:'😀',2:'😁',-1:'😟',-2:'😡'}
    labels = list(map(lambda s: emojies[s/s*2] if abs(s) >= 0.5 else (emojies[s/s] if s > 0 else emojies[s]),sentiments))
    for x, y, l in zip(range(len(sentiments)), sentiments, labels):
        ax.annotate(l, xy=(x, y), xytext=(0, np.sign(y)*10),
                    textcoords="offset points", ha="center")    

def sentimentReport(sentiments):
    with plt.xkcd():
        fig = plt.figure()
        ax = fig.add_axes([0,0,1,1])
        rects = ax.stem(sentiments)
        ax.set_xlabel('Messages')
        ax.set_ylim([-1,1])
        ax.set_ylabel('Positivity')
        ax.set_title('Sentiment analysis')
        emojiAutolabel(ax,sentiments)
        plt.show()