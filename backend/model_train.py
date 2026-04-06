import os
import argparse
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset
import evaluate
import numpy as np

def compute_metrics(eval_pred):
    metric = evaluate.load("accuracy")
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)

def train_model(model_name="bert-base-uncased"):
    print(f"Training high-performance Fake News model using: {model_name}")
    
    # 1. Load fine-tuning fake news dataset
    # Using 'GonzaloA/fake_news' which is a standard well-known fake news dataset on Hugging Face (Real/Fake classes)
    print("Loading fine-tuned fake news dataset...")
    try:
        dataset = load_dataset("GonzaloA/fake_news", split="train[:2000]") # Limit for demonstration
    except Exception as e:
        print(f"Could not load primary dataset: {e}. Falling back to a standard text classification dataset.")
        dataset = load_dataset("mteb/tweet_sentiment_extraction", split="train[:2000]")
        
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=128)

    print("Tokenizing dataset...")
    tokenized_datasets = dataset.map(tokenize_function, batched=True)
    
    # Split dataset
    split = tokenized_datasets.train_test_split(test_size=0.2)
    train_dataset = split["train"]
    eval_dataset = split["test"]

    # 2. Initialize Model
    print(f"Initializing {model_name} for sequence classification...")
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

    # 3. Setup Training Arguments
    output_dir = f"./results-{model_name.replace('/', '-')}"
    training_args = TrainingArguments(
        output_dir=output_dir,
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=8 if "roberta" not in model_name else 4, # Smaller batch for Roberta-large
        per_device_eval_batch_size=8,
        num_train_epochs=3,
        weight_decay=0.01,
        save_total_limit=2,
    )

    # 4. Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        compute_metrics=compute_metrics,
    )

    print("Starting fine-tuning...")
    trainer.train()

    # 5. Save final model
    save_path = f"./fake_news_{model_name.split('/')[-1]}"
    print(f"Saving fine-tuned model to {save_path}")
    trainer.save_model(save_path)
    tokenizer.save_pretrained(save_path)
    print("Training complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune Transformer models for Fake News Detection")
    parser.add_argument("--model", type=str, default="bert-base-uncased", choices=["bert-base-uncased", "roberta-large"], help="Transformer model architecture to fine-tune")
    args = parser.parse_args()
    
    train_model(args.model)
