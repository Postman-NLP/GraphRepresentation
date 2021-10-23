import argparse
import logging
import os
import pickle
import networkx as nx
from Node2VecWalk import GenerateWalks
from gensim.models import Word2Vec


def GetLogger():
    _logger = logging.getLogger()
    _logger.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt="[ %(asctime)s ] %(message)s", datefmt="%a %b %d %H:%M:%S %Y")
    # set handler
    sHandler = logging.StreamHandler()
    sHandler.setFormatter(formatter)
    # add handler
    _logger.addHandler(sHandler)
    return _logger


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', default="BlogCatalog")
    parser.add_argument('--length', type=int, default=80)
    parser.add_argument('--per_num', type=int, default=10)
    parser.add_argument('--min_count', type=int, default=0)
    parser.add_argument('--emb_size', type=int, default=128)
    parser.add_argument('--window_size', type=int, default=10)
    parser.add_argument('--workers', type=int, default=4)

    parser.add_argument('--p', type=float, default=2)
    parser.add_argument('--q', type=float, default=0.5)
    args = parser.parse_args()
    logger = GetLogger()
    # using nx.DiGraph create graph
    graph = nx.read_edgelist(f"../data/{args.dataset}/{args.dataset}_edges.txt",
                             create_using=nx.DiGraph(), data=[("weight", float)])
    if not nx.is_weighted(graph):
        nx.set_edge_attributes(graph, values=1.0, name='weight')
    if args.dataset in ["BlogCatalog"]:
        graph = graph.to_undirected()
    if not os.path.isfile(f"node2vec_{args.per_num}_{args.length}.txt"):
        walks = GenerateWalks(args.per_num, args.length, graph)
        pickle.dump(walks, open(f"node2vec_{args.per_num}_{args.length}.txt", 'wb'))
    else:
        walks = pickle.load(open(f"node2vec_{args.per_num}_{args.length}.txt", 'rb'))
    logger.info("generate walks done!")
    # skip-gram --- hierarchical softmax
    model = Word2Vec(sentences=walks, min_count=args.min_count, vector_size=args.emb_size, window=args.window_size,
                     workers=args.workers, sg=1)
    logger.info("train Node2Vec done!")
