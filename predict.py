from simpletransformers.seq2seq import Seq2SeqModel
import re

text = ''  # input

mname = "./mbart"

model_args = {
    "reprocess_input_data": True,
    "overwrite_output_dir": True,
    "max_seq_length": 172,
    "train_batch_size": 2,
    "num_train_epochs": 1,
    "save_eval_checkpoints": False,
    "save_model_every_epoch": False,
    "evaluate_generated_text": True,
    "evaluate_during_training_verbose": True,
    "use_multiprocessing": False,
    "max_length": 172,
    "manual_seed": 4,
    "save_steps": -1,
}
model_rewrite = Seq2SeqModel(
    encoder_decoder_type="mbart",
    encoder_decoder_name=mname,
    args=model_args,
    use_cuda=False,
)

predict = model_rewrite.predict([text])
predict = " ".join(predict)

pat = r"в (понедельник|вторник|среду|четверг|пятницу|субботу|воскресенье), " \
      r"[0-9]+ (января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря), "
predict = re.sub(pat, '', predict)

print(predict)
