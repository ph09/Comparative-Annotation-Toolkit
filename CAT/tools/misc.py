"""
Miscellaneous tools for the pipeline. Some may eventually be refactored into their own modules.
"""
import pandas as pd


def read_attributes_tsv(attrs_path):
    """
    Loads the attributes TSV into a pandas DataFrame
    :param attrs_path: path to attributes file generated by Gff3ToAttrs
    :return: DataFrame
    """
    return pd.read_csv(attrs_path, sep='\t', header=0, index_col=0)
