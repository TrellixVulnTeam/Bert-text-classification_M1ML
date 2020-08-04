import torch
import torch.nn as nn
from pytorch_pretrained import BertModel, BertTokenizer



class Config(object):
    """
    配置参数
    """
    def __init__(self, dataset):
        self.model_name = 'BruceBert'        
        self.train_path = dataset + '/data/train.txt'
        self.test_path = dataset + '/data/test.txt'
        self.dev_path = dataset + '/data/dev.txt'
        # dataset
        self.datasetpkl = dataset + '/data/dataset.pkl'
        # 类别 
        self.class_list = [x.strip() for x in open(dataset + '/data/class.txt').readlines()]
        #训练完模型后的保存地址
        self.save_path = dataset + '/saved_dict/' + self.model_name + '.ckpt'
        # 设备配置
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        # 若超过1000个bacth效果还没有提升，提前结束训练
        self.require_improvement = 1000

        # 类别数
        self.num_classes = len(self.class_list)
        self.num_epochs = 3
        self.batch_size = 128
        self.learning_rate = 1e-5
        # 每句话处理的长度(短填，长切）
        self.pad_size = 32

        # 加载bert预训练模型的位置
        self.bert_path = 'bert_pretrain'
        # bert切词器
        self.tokenizer = BertTokenizer.from_pretrained(self.bert_path)
        # bert隐层层个数，基础bert
        self.hidden_size = 768


class Model(nn.Module):

    def __init__(self, config):
        super(Model, self).__init__()
        #加载预训练里的bert
        self.bert = BertModel.from_pretrained(config.bert_path)
        #True可以对bert的参数进行微调fine-tuning
        for param in self.bert.parameters():
            param.requires_grad = True
        self.fc = nn.Linear(config.hidden_size, config.num_classes)

    def forward(self, x):   # x: tarin_iter
        # x [ids, seq_len, mask]
        context = x[0]        #对应输入的句子 shape[128,32]
        mask = x[2]           #对padding部分进行mask shape[128,32]

        #经过bert层的输出，shape [128,768]
        _, pooled = self.bert(context, attention_mask=mask, output_all_encoded_layers=False)  
        out = self.fc(pooled)    # shape [128,10]
        return out


