# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments

# ---------------- 1. Load dataset ----------------
df = pd.read_csv('movie_comments.csv')

train_df, val_df = train_test_split(df, test_size=0.2, random_state=690, stratify=df['sentiment'])


# ---------------- 2. Define custom dataset class ----------------
class CommentDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]

        # Tokenize the text
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        # Convert to tensor and remove extra batch dimension
        item = {key: encoding[key].squeeze(0) for key in encoding}
        item['labels'] = torch.tensor(label, dtype=torch.long)
        return item


# ---------------- 3. Load pre-trained BERT model and tokenizer ----------------
model_name = "bert-base-cased"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)

# ---------------- 4. Prepare training and validation datasets ----------------
max_length = 256
train_dataset = CommentDataset(
    texts=train_df['comment_content'].tolist(),
    labels=train_df['sentiment'].tolist(),
    tokenizer=tokenizer,
    max_length=max_length
)
val_dataset = CommentDataset(
    texts=val_df['comment_content'].tolist(),
    labels=val_df['sentiment'].tolist(),
    tokenizer=tokenizer,
    max_length=max_length
)


# ---------------- 5. Define evaluation function ----------------
def compute_metrics(pred):
    labels = pred.label_ids
    preds = np.argmax(pred.predictions, axis=1)
    acc = accuracy_score(labels, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average="binary")
    return {"accuracy": acc, "precision": precision, "recall": recall, "f1": f1}


# ---------------- 6. Set training arguments ----------------
training_args = TrainingArguments(
    output_dir='results',
    num_train_epochs=3,
    per_device_train_batch_size=64,
    per_device_eval_batch_size=64,
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_dir='logs',
    logging_steps=50,
    log_level="info",
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    seed=690,
)

# ---------------- 7. Start training ----------------
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
)

if __name__ == '__main__':
    trainer.train()
    eval_results = trainer.evaluate()
    print("Evaluation results:")
    print(eval_results)
