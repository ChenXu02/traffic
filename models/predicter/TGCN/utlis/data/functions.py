import numpy as np
import pandas as pd
import torch


def load_features(feat_path,feat_path2, dtype=np.float32):
    #feat_df = pd.read_csv(feat_path)
    #feat = np.array(feat_df, dtype=dtype)
    feat = np.load(feat_path)[:,0,:].transpose(1,0)
    feat2 = feat#np.load(feat_path2)[:, 0, :].transpose(1, 0)

    return feat,feat2


def load_adjacency_matrix(adj_path, dtype=np.float32):
    #adj_df = pd.read_csv(adj_path, header=None)
    #adj = np.array(adj_df, dtype=dtype)
    adj=np.load(adj_path)
    return adj


def generate_dataset(
    data2,data, seq_len, pre_len, time_len=None, split_ratio=0.8, normalize=True
):
    """
    :param data: feature matrix with missing data
    :param data2: feature matrix
    :param seq_len: length of the train data sequence
    :param pre_len: length of the prediction data sequence
    :param time_len: length of the time series in total
    :param split_ratio: proportion of the training set
    :param normalize: scale the data to (0, 1], divide by the maximum value in the data
    :return: train set (X, Y) and test set (X, Y)
    """
    if time_len is None:
        time_len = data.shape[0]
    if normalize:
        max_val = [np.mean(data),np.std(data)]
        max_val2 = [np.mean(data2),np.std(data2)]
        data = (data-max_val[0]) / max_val[1]
        data2 = (data2-max_val2[0]) / max_val2[1]
    train_size = int(time_len * split_ratio)
    train_data = data[:train_size]
    test_data = data[train_size:time_len]
    test_data2 = data2[train_size:time_len]
    train_X, train_Y, test_X, test_Y = list(), list(), list(), list()
    for i in range(len(train_data) - seq_len - pre_len):
        train_X.append(np.array(train_data[i : i + seq_len]))
        train_Y.append(np.array(train_data[i + seq_len : i + seq_len + pre_len]))
    for i in range(len(test_data) - seq_len - pre_len):
        test_X.append(np.array(test_data[i : i + seq_len]))
        test_Y.append(np.array(test_data2[i + seq_len : i + seq_len + pre_len]))
    return np.array(train_X), np.array(train_Y), np.array(test_X), np.array(test_Y)


def generate_torch_datasets(
    data,data2, seq_len, pre_len, time_len=None, split_ratio=0.8, normalize=True
):
    train_X, train_Y, test_X, test_Y = generate_dataset(
        data,
        data2,
        seq_len,
        pre_len,
        time_len=time_len,
        split_ratio=split_ratio,
        normalize=normalize,
    )
    train_dataset = torch.utils.data.TensorDataset(
        torch.FloatTensor(train_X), torch.FloatTensor(train_Y)
    )
    test_dataset = torch.utils.data.TensorDataset(
        torch.FloatTensor(test_X), torch.FloatTensor(test_Y)
    )
    return train_dataset, test_dataset
