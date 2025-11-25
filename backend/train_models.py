import pandas as pd
import spacy
import tensorflow as tf
from tensorflow.keras.layers import TextVectorization, Embedding, Bidirectional, LSTM, Dropout, Dense
from tensorflow.keras.models import Sequential
from sklearn.model_selection import train_test_split
import numpy as np
import os

def preprocess_text(text, nlp):
    if pd.isna(text):
        return ""
    doc = nlp(str(text).lower())
    tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
    return " ".join(tokens)

def train_and_save_model():
    df = pd.read_csv('data/songs.csv') # Adjusted path

    try:
        nlp = spacy.load('en_core_web_sm')
    except OSError:
        print('Downloading language model for the first time. This may take a few minutes.')
        from spacy.cli import download
        download('en_core_web_sm')
        nlp = spacy.load('en_core_web_sm')


    print("Preprocessing text...")
    df['clean_lyrics'] = df['Lyrics'].apply(lambda text: preprocess_text(text, nlp))

    X_text = df['clean_lyrics']
    y = df['AgeAppropriate']

    X_train_text, _, y_train_text, _ = train_test_split(
        X_text, y, test_size=0.2, random_state=42, stratify=y
    )

    MAX_SEQUENCE_LENGTH = 40
    EMBEDDING_DIM = 20
    MAX_WORDS = 1000

    vectorize_layer = TextVectorization(
        max_tokens=MAX_WORDS,
        output_mode='int',
        output_sequence_length=MAX_SEQUENCE_LENGTH
    )

    print("Building vocabulary using TextVectorization...")
    vectorize_layer.adapt(X_train_text.to_list())
    vocab_size = len(vectorize_layer.get_vocabulary())
    print(f"Vocabulary Size: {vocab_size}")

    model_lstm_native = Sequential()
    model_lstm_native.add(tf.keras.Input(shape=(1,), dtype=tf.string))
    model_lstm_native.add(vectorize_layer)
    model_lstm_native.add(Embedding(input_dim=vocab_size,
                                     output_dim=EMBEDDING_DIM,
                                     mask_zero=True))
    model_lstm_native.add(Bidirectional(LSTM(
        3,
        recurrent_dropout=0.2,
        kernel_regularizer=tf.keras.regularizers.l2(0.1)
    )))
    model_lstm_native.add(Dropout(0.3))
    model_lstm_native.add(Dense(1, activation='sigmoid'))

    model_lstm_native.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.1),
                             loss='binary_crossentropy',
                             metrics=['accuracy'])
    model_lstm_native.build(input_shape=(None, 1))
    model_lstm_native.summary()

    print("\nStarting LSTM Model Training...")

    BATCH_SIZE = 64

    train_dataset = tf.data.Dataset.from_tensor_slices(
        (X_train_text.to_list(), y_train_text)
    ).shuffle(10000).batch(BATCH_SIZE).cache().prefetch(tf.data.AUTOTUNE)

    model_lstm_native.fit(
        train_dataset,
        epochs=4,
        verbose=1
    )

    model_dir = 'saved_model'
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    model_path = os.path.join(model_dir, 'lyrics_model.keras')
    model_lstm_native.save(model_path)
    print(f"Model saved to {model_path}")

if __name__ == '__main__':
    train_and_save_model()
