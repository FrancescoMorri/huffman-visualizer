from anytree import Node
from anytree.exporter import DotExporter
import streamlit as st
import numpy as np
import pandas as pd
import sys

def sort_dict(unsorted_dict):
    return {k: v for k, v in sorted(unsorted_dict.items(), key=lambda item: item[1]['freq'])}

def get_children(node, encoding, final_dict):
    try:
        get_children(node.children[0], encoding=encoding+"0",final_dict=final_dict)
        get_children(node.children[1], encoding=encoding+"1",final_dict=final_dict)
    except:
        final_dict[node.name] = encoding

def encode_sentence(sentence, encoding):
    encoded_sentence = ""
    for c in sentence:
        encoded_sentence += encoding[c]
    return encoded_sentence

def compute_entropy(totlen, text_dict, encoding_dict):
    entropy = 0
    huffman_weight = 0
    for k in encoding_dict.keys():
        w = text_dict[k]['freq']/totlen
        entropy -= w*np.log2(w)
        huffman_weight += w*len(encoding_dict[k])
    return entropy, huffman_weight

st.set_page_config(page_title="Huffman Encoding", page_icon="random",
                 layout="wide", initial_sidebar_state="auto", menu_items=None)

st.title("Huffman Encoding Generator")
st.caption("The app will generate the encoding, produce an image of the binary tree used and compute the Shannon entropy of the original sentence, in order to check how close the encoding is to optimality.")
st.caption("To highlight spaces in the image I suggest to use '-' instead of ' '. Also to keep things less messy, all characters are put in lower case.")
DATA = ""

with st.form("B"):
    DATA = st.text_input(label="Write the sentence you want to encode:")
    DATA = DATA.lower()
    pre_dict = {}
    for d in DATA:
        if d in pre_dict.keys():
            pre_dict[d]['freq'] += 1
            pre_dict[d]['node'].freq += 1
        else:
            pre_dict[d] = {'freq':1, 'node':Node(d, char=d, weight=None, freq=1)}

    sorted_dict = sort_dict(pre_dict)
    i = len(sorted_dict.keys())

    while i > 1:
        c1 = list(sorted_dict.keys())[0]
        c2 = list(sorted_dict.keys())[1]
        n1 = sorted_dict[c1]['freq']
        n2 = sorted_dict[c2]['freq']
        sorted_dict[c1]['node'].weight = '0'
        sorted_dict[c2]['node'].weight = '1'
        n_t = n1+n2
        c_t = c1+c2
        sorted_dict[c_t] = {'freq':n_t, 'node':Node(c_t, children=[sorted_dict[c1]['node'], sorted_dict[c2]['node']], char=c_t, freq=n_t)}
        sorted_dict.pop(c1, None)
        sorted_dict.pop(c2, None)
        i = len(sorted_dict.keys())
        sorted_dict = sort_dict(sorted_dict)

    print_out = st.form_submit_button("Encode!")



if print_out:
    full_tree = sorted_dict[list(sorted_dict.keys())[0]]['node']
    final_dict = {}
    encoding = ""
    get_children(full_tree, encoding, final_dict)
    st.subheader("Binary Encoding:")
    binary_sentence = encode_sentence(DATA, final_dict)
    st.text(binary_sentence)
    DotExporter(full_tree,
                nodenamefunc=lambda node: "Char:%s, Freq:%s"%(node.name,node.freq),
                nodeattrfunc=lambda node: "shape=box",
                edgeattrfunc=lambda parent, child: "style=bold,label=%s" % (child.weight or 0)
    ).to_dotfile("tree.dot")
    with open("tree.dot", 'r') as f:
        tree_file = f.read()
    st.subheader("Tree Graph:")
    st.graphviz_chart(tree_file)
    H, L = compute_entropy(len(DATA), pre_dict, final_dict)
    initial_size = sys.getsizeof(DATA)
    df = pd.DataFrame([[H,L,initial_size,len(binary_sentence)]],columns=['entropy','encoding','original size (byte)','compressed size (byte)'])
    st.subheader("Difference from entropy:")
    st.dataframe(df)