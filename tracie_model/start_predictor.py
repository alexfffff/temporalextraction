import torch
from torch.utils.data.dataloader import DataLoader
from transformers import (
    AutoTokenizer,
    PreTrainedTokenizer,
    T5ForConditionalGeneration,
)
from torch.utils.data.sampler import SequentialSampler
from transformers.data.data_collator import DataCollator
from torch.utils.data.dataset import Dataset
from typing import Dict
from dataclasses import dataclass

@dataclass
class CustomDataCollator(DataCollator):
    def collate_batch(self, features) -> Dict[str, torch.Tensor]:
        input_ids = torch.tensor([f['input_ids'] for f in features], dtype=torch.long)
        attention_mask = torch.tensor([f['attention_mask'] for f in features], dtype=torch.long)
        lm_labels = torch.tensor([f['lm_labels'] for f in features], dtype=torch.long)
        decoder_attention_mask = torch.tensor([f['decoder_attention_mask'] for f in features], dtype=torch.long)

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "lm_labels": lm_labels,
            "decoder_attention_mask": decoder_attention_mask,
        }

class LineByLineTextDataset(Dataset):
    """
    This will be superseded by a framework-agnostic approach
    soon.
    """

    def __init__(self, tokenizer: PreTrainedTokenizer, lines):

        originals = []
        labels = []
        for l in lines:
            originals.append(l.split("\t")[0])
            labels.append(l.split("\t")[1])

        self.inputs = tokenizer.batch_encode_plus(originals, pad_to_max_length=True)
        self.labels = tokenizer.batch_encode_plus(labels, pad_to_max_length=True)

    def __len__(self):
        return len(self.inputs["input_ids"])

    def __getitem__(self, i):
        source_ids = self.inputs["input_ids"][i]
        target_ids = self.labels["input_ids"][i]
        src_mask = self.inputs["attention_mask"][i]
        target_mask = self.labels["attention_mask"][i]
        return {"input_ids": source_ids, "attention_mask": src_mask, "lm_labels": target_ids, "decoder_attention_mask": target_mask}


def get_dataset(lines, tokenizer):
    ret = LineByLineTextDataset(tokenizer=tokenizer, lines=lines)
    return ret


class Predictor:

    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = ""
        self.model = T5ForConditionalGeneration.from_pretrained(
            "/shared/public/ben/start_point_35k"
        ).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained("t5-large")
        self.model.resize_token_embeddings(len(self.tokenizer))
        self.model.eval()
        self.data_collator = CustomDataCollator()

    # Input: a list of lines
    def predict(self, lines):
        eval_dataset = get_dataset(lines, self.tokenizer)
        sampler = SequentialSampler(eval_dataset)
        data_loader = DataLoader(
            eval_dataset,
            sampler=sampler,
            batch_size=4,
            collate_fn=self.data_collator.collate_batch,
        )
        ret = []
        for inputs in data_loader:
            for k, v in inputs.items():
                inputs[k] = v.to(self.device)
            with torch.no_grad():
                outputs = self.model.generate(
                    input_ids=inputs['input_ids'],
                    attention_mask=inputs['attention_mask'],
                    max_length=4,
                )
                dec = [self.tokenizer.decode(ids) for ids in outputs]
                if dec[2] == "positive":
                    ret.append(1)
                elif dec[2] == "negative":
                    ret.append(-1)
                else:
                    ret.append(0)

        return ret

