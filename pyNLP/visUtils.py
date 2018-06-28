from sklearn.manifold import TSNE

#todo switch to umap
def textVectorTSNEPlot(labels, features):
    """
    :param labels: list of strings
    :param features: list of vectors
    :return: plot 2d points of each vector with text label
    """
    X_embedded = TSNE(n_components=2, perplexity=6).fit_transform(features)
    import matplotlib.pyplot as plt
    (fig, ax) = plt.subplots(figsize=(25, 16))
    ax.scatter(X_embedded[:, 0], X_embedded[:, 1], c="b")
    for i, txt in enumerate(labels):
        ax.annotate(txt, (X_embedded[i, 0] + .75, X_embedded[i, 1]))