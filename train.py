import pandas as pd
from simpletransformers.seq2seq import Seq2SeqModel
import nltk

nltk.download('punkt')

df = pd.read_csv('./paral_news.csv')
df = df.sample(frac=1).reset_index(drop=True)
print(df.shape)


def clean_text(text):
    text = str(text)
    text = nltk.sent_tokenize(text)[:6]
    text = ' '.join(text)
    return text


df['text1'] = df.apply(lambda x: clean_text(x['text1']), axis=1)
df['text2'] = df.apply(lambda x: clean_text(x['text2']), axis=1)

df['input_text'] = df['text1']
df['target_text'] = df['text2']

model_args = {
    "reprocess_input_data": True,
    "overwrite_output_dir": True,
    "max_seq_length": 150,
    "train_batch_size": 2,
    "num_train_epochs": 1,
    "save_eval_checkpoints": False,
    "save_model_every_epoch": False,
    "evaluate_generated_text": True,
    "evaluate_during_training_verbose": True,
    "use_multiprocessing": False,
    "max_length": 150,
    "manual_seed": 4,
    "save_steps": -1,
}


model = Seq2SeqModel(
    encoder_decoder_type="mbart",
    encoder_decoder_name="facebook/mbart-large-cc25",
    args=model_args,
    use_cuda=True,
)

model.train_model(df)
