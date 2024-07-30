import tkinter as tk
from tkinter import scrolledtext, messagebox
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
import os


# Preprocess text data
def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    words = nltk.word_tokenize(text)
    words = [lemmatizer.lemmatize(word.lower()) for word in words if word.isalnum() and word.lower() not in stop_words]
    return ' '.join(words)

# Load data from the specified path
def load_data(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found.")
    
    df = pd.read_csv(file_path)
    if 'Document' not in df.columns or 'Cluster' not in df.columns or 'Cluster Name' not in df.columns:
        raise ValueError("CSV file must contain 'Document', 'Cluster', and 'Cluster Name' columns.")
    
    return df

# Train K-Means clustering model
def train_model(df):
    documents = df['Document'].tolist()
    clusters = df['Cluster'].tolist()
    
    processed_docs = [preprocess_text(doc) for doc in documents]

    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    X = vectorizer.fit_transform(processed_docs)

    kmeans = KMeans(n_clusters=len(set(clusters)), random_state=42)
    kmeans.fit(X)

    return kmeans, vectorizer

# Predict cluster for new documents
def predict_category(model, vectorizer, new_docs):
    processed_docs = [preprocess_text(doc) for doc in new_docs]
    X = vectorizer.transform(processed_docs)
    return model.predict(X)

# Save clustering results to CSV
def save_to_csv(file_path, documents, predictions, cluster_names):
    df = pd.DataFrame({'Document': documents, 'Cluster': predictions})
    df['Cluster Name'] = df['Cluster'].map(cluster_names)
    
    if os.path.exists(file_path):
        # Append data to existing CSV file
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        # Create new CSV file
        df.to_csv(file_path, index=False)
    print(f"Data saved to {file_path}")

class DocumentClusteringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Document Clustering")

        self.label = tk.Label(root, text="Enter news articles (separate articles with double newlines):")
        self.label.pack()

        self.text_area = scrolledtext.ScrolledText(root, width=50, height=20)
        self.text_area.pack()

        self.cluster_button = tk.Button(root, text="Cluster Documents", command=self.cluster_documents)
        self.cluster_button.pack()

        self.result_label = tk.Label(root, text="")
        self.result_label.pack()

        # Load data and train model
        try:
            print("Loading data and training model...")
            self.df = load_data(r'clustered_documents_bbc.csv')
            self.model, self.vectorizer = train_model(self.df)
            self.cluster_names = dict(self.df[['Cluster', 'Cluster Name']].drop_duplicates().values)
            print("Model trained successfully.")
        except Exception as e:
            messagebox.showerror("Initialization Error", str(e))
            self.root.destroy()

    def cluster_documents(self):
        content = self.text_area.get("1.0", tk.END).strip()
        documents = [doc.strip() for doc in content.split('\n\n') if doc.strip()]
        if not documents:
            messagebox.showwarning("Input Error", "Please enter some news articles to cluster.")
            return

        clusters = predict_category(self.model, self.vectorizer, documents)
        save_to_csv(r'clustered_documents_bbc.csv', documents, clusters, self.cluster_names)
        result_text = ""
        for doc, cluster in zip(documents, clusters):
            cluster_name = self.cluster_names.get(cluster, "Unknown")
            result_text += f"Cluster {cluster} ({cluster_name}):\n{doc}\n\n"

        self.result_label.config(text=result_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = DocumentClusteringApp(root)
    root.mainloop()