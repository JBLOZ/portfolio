<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> 42fa237a0948d1ceb29232ede3f74fd9ab574339
import sentiment_analysis

# Inicializa el analizador de sentimiento
analizador = sentiment_analysis.SentimentAnalysisSpanish()

# Analiza una frase
texto_positivo = "Me encanta este producto, es de una calidad excelente."
sentimiento_pos = analizador.sentiment(texto_positivo)
print(f"Texto: '{texto_positivo}'")
print(f"Puntuación de sentimiento: {sentimiento_pos}")

texto_negativo = "El servicio fue terrible, no lo recomiendo para nada."
sentimiento_neg = analizador.sentiment(texto_negativo)
print(f"\nTexto: '{texto_negativo}'")
<<<<<<< HEAD
print(f"Puntuación de sentimiento: {sentimiento_neg}")
=======
print(f"Puntuación de sentimiento: {sentimiento_neg}")
=======
from transformers import BertModel, BertTokenizer, AdamW, get_linear_schedule_with_warmup
import torch
import numpy as np
from sklearn.model_selection import train_test_split
from torch import nn, optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from textwrap import wrap
# from primaryapp.IMDBDataset import IMDBDataset
from BERTSentimentClassifier import BERTSentimentClassifier
#import translate as trs
#from multiprocessing import Process, freeze_support



#INICIALIZACIÓN
RANDOM_SEED = 42
MAX_LEN = 100
BATCH_SIZE = 16
DATASET_PATH = 'primaryapp/BERT_sentiment_IMDB_Dataset.csv'
NCLASSES = 2

np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu") 

torch.cuda.empty_cache()
torch.cuda.is_available()
torch.cuda.current_device()
torch.cuda.memory_summary()

#print(torch.cuda.get_device_name(0))
#print(device)

#df = pd.read_csv(DATASET_PATH)
#df = df[0: 10000]

# REAJUSTAR DATASET
#df['label'] = (df['sentiment']=='positive').astype(int)
#df.drop('sentiment', axis=1, inplace=True)

# TOKENIZACIÓN
PRE_TRAINED_MODEL_NAME = 'bert-base-cased'
tokenizer = BertTokenizer.from_pretrained(PRE_TRAINED_MODEL_NAME)

# EJEMPLO DE TOKENIZACIÓN
'''sample_txt = "I really loved that movie. I don´t liked that love movie but it was not very bad"

tokens = tokenizer.tokenize(sample_txt)
token_ids = tokenizer.convert_tokens_to_ids(tokens)
print('Frase: ', sample_txt)
print('Tokens: ', tokens)
print('Tokens numericos: ', token_ids)

# CODIFICACIÓN PARA INTRODUCIR A BERT
encoding = tokenizer.encode_plus(
    sample_txt,
    max_length = 50,
    truncation = True,
    add_special_tokens = True,
    return_token_type_ids = False,
    padding = 'max_length',
    return_attention_mask = True,
    return_tensors = 'pt'
)

print(encoding.keys())

print(tokenizer.convert_ids_to_tokens(encoding['input_ids'][0]))
print(encoding['input_ids'][0])
print(encoding['attention_mask'][0])
'''
# DATA LOADER:
'''def data_loader(df, tokenizer, max_len, batch_size):
    dataset = IMDBDataset (
        reviews = df.review.to_numpy(),
        labels = df.label.to_numpy(),
        tokenizer = tokenizer,
        max_len = MAX_LEN
    )

    return DataLoader(dataset, batch_size = BATCH_SIZE, num_workers = 4)

# División de datos de entrenamiento y datos de prueba
df_train, df_test = train_test_split(df, test_size = 0.2, random_state = RANDOM_SEED)

train_data_loader = data_loader(df_train, tokenizer, MAX_LEN, BATCH_SIZE)
test_data_loader = data_loader(df_test, tokenizer, MAX_LEN, BATCH_SIZE)
'''
#if __name__== '__main__':


model = BERTSentimentClassifier(NCLASSES)
model = model.to(device)

# ENTRENAMIENTO
'''EPOCHS = 4
optimizer = AdamW(model.parameters(), lr=2e-5, correct_bias = False)
total_steps = len(train_data_loader) * EPOCHS
scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps = 0,
    num_training_steps = total_steps
)
loss_fn = nn.CrossEntropyLoss().to(device)
'''
'''
#Iteración del entrenamiento
def train_model(model, data_loader, loss_fn, optimizer, device, scheduler, n_examples):
    model = model.train()
    losses = []
    correct_predictions = 0
    for batch in data_loader:
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['label'].to(device)
        outputs = model(input_ids = input_ids, attention_mask = attention_mask)
        _, preds = torch.max(outputs, dim = 1)
        loss = loss_fn(outputs, labels)
        correct_predictions += torch.sum(preds == labels)
        losses.append(loss.item())
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        scheduler.step()
        optimizer.zero_grad()
    return correct_predictions.double()/n_examples, np.mean(losses)

def eval_model(model, data_loader, loss_fn, device, n_examples):
    model = model.eval()
    losses = []
    correct_predictions = 0
    with torch.no_grad():
        for batch in data_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)
            outputs = model(input_ids = input_ids, attention_mask = attention_mask)
            _, preds = torch.max(outputs, dim=1)
            loss = loss_fn(outputs, labels)
            correct_predictions += torch.sum(preds == labels)
            losses.append(loss.item())
    return correct_predictions.double()/n_examples, np.mean(losses)
'''
model = torch.load('40model_amazon.pt')
#print(model.eval())

def classifySentiment(review_text):
    encoding_review = tokenizer.encode_plus(
        review_text,
        max_length = MAX_LEN,
        truncation = True,
        add_special_tokens = True,
        return_token_type_ids = False,
        padding = 'max_length',
        return_attention_mask = True,                               
        return_tensors = 'pt'
    )

    input_ids = encoding_review['input_ids'].to(device)
    attention_mask = encoding_review['attention_mask'].to(device)
    output = model(input_ids, attention_mask)
    _, prediction = torch.max(output, dim = 1)
    #print("\n".join(wrap(review_text)))    
    #sentimiento = 'nada'
    '''sentimiento = 0
    if prediction:
        #sentimiento = 'Sentimiento positivo: * * * * *'         
        sentimiento = 1
    else:
        #sentimiento = 'Sentimiento negativo: *'
        sentimiento = 0

    return int(sentimiento)'''
    return prediction

'''
#answer = trs.translate('hoy fue un mal dia')
answer = 'today was a good day'

sentimiento = classifySentiment(answer)

#print(answer)
print(sentimiento)
'''
>>>>>>> 3b028249 (modelo)
>>>>>>> 42fa237a0948d1ceb29232ede3f74fd9ab574339
