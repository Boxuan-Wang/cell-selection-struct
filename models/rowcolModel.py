import torch
from torch.utils.data import Dataset, DataLoader, random_split, SequentialSampler
import os
import pandas as pd
from torch import optim, nn, utils, Tensor
import lightning.pytorch as pl
from transformers import BertTokenizer, BertModel

MAX_LEN = 256

class ColRowClassifier(pl.LightningModule):
  def __init__(self,lr = 3e-5):
    super().__init__()
    self.lr = lr
    self.softmax = nn.Softmax(dim=1)
    self.bert_model = BertModel.from_pretrained('bert-base-uncased')
    self.classify = nn.Sequential(nn.Flatten(),nn.Dropout(p=0.1),nn.Linear(768*MAX_LEN,2))

  def forward(self, x):
    input_ids = x['input_ids']
    input_ids = input_ids.view(input_ids.size(0),-1)
    attn_mask = x['attention_mask']
    attn_mask = attn_mask.view(attn_mask.size(0),-1)
    
    bert_output = self.bert_model(input_ids = input_ids, attention_mask = attn_mask)
    y = self.classify(bert_output.last_hidden_state)
    return y

  def training_step(self, batch, batch_idx):
    x, verdict = batch
    y = self.forward(x)
    loss = nn.CrossEntropyLoss()
    loss = loss(y,verdict)
    self.log("train_loss", loss, on_epoch=True)
    return loss

  def configure_optimizers(self):
    optimizer = optim.Adam(self.parameters(),lr=self.lr)
    return optimizer

  def validation_step(self, val_batch, batch_idx):
    x, verdict = val_batch
    y = self.forward(x)
    loss = nn.CrossEntropyLoss()
    loss = loss(y,verdict)
    self.log('val_loss',loss)

    return loss
  
  def predict(self, x):
    logits = self.forward(x)
    return self.softmax(logits).cpu().numpy()[0][0]
 
def tokenize(text:str, tokenizer:BertTokenizer) -> Tensor:
  return tokenizer(
            text, 
            add_special_tokens = True,
            max_length = MAX_LEN,
            padding = 'max_length',
            return_token_type_ids = True,
            truncation = True,
            return_attention_mask = True,
            return_tensors = 'pt')
  
class ColRowDataset(Dataset):
  def __init__(self, csv_path: str, tokenizer: BertTokenizer,size_limit:int = None):
    self.size_limit = size_limit
    self.df = pd.read_csv(csv_path, names=['text','verdict'])
    if size_limit is not None:
      self.df = self.df[:size_limit]
    text_tensors = [tokenize(text,tokenizer) for text in self.df['text']]
    verdict_tensors = self.df['verdict'].map(lambda b: torch.Tensor([1.0, 0.0]) if b else torch.Tensor([.0, 1.0]))
    # rev_verdict = 1 - self.df['verdict']
    # verdict_tensors = torch.Tensor(self.df['verdict'], rev_verdict)
    self.tensors = (text_tensors, verdict_tensors)
    
  def __len__(self) -> int:
    return len(self.tensors[0])
  
  def __getitem__(self, index:int):
    return tuple(item[index] for item in self.tensors)
  
  def head(self, n:int):
    return self.df[:n]

def get_dataloaders(src_dataset: Dataset, batch_size:int = 32, split:bool = False) -> DataLoader:
  if split:
    ds_t, ds_v = random_split(src_dataset, [0.9,0.1], generator=torch.Generator().manual_seed(2023))
    dataloader_t = DataLoader(
        ds_t, 
        sampler = SequentialSampler(ds_t),
        batch_size = batch_size,
        num_workers = 8)
    dataloader_v = DataLoader(
        ds_v, 
        sampler = SequentialSampler(ds_v),
        batch_size = batch_size,
        num_workers = 8)
    return dataloader_t, dataloader_v
  else:
    dataloader = DataLoader(
        src_dataset,
        sampler = SequentialSampler(src_dataset),
        batch_size = batch_size,
        num_workers = 8)
    return dataloader