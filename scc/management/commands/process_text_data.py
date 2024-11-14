from django.core.management.base import BaseCommand
import os
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from django.conf import settings

class Command(BaseCommand):
    help = 'Process text data, extract features, and save TfidfVectorizer'

    def handle(self, *args, **kwargs):
        # Path to the CSV file
        csv_path = os.path.join(settings.BASE_DIR, 'dataset', 'Skin_text_classifier.csv')
        
        # Load the data
        df = pd.read_csv(csv_path)

        # Initialize the vectorizer
        vectorizer = TfidfVectorizer(max_features=5000)

        # Transform the text data (use the correct column name 'Text')
        text_features = vectorizer.fit_transform(df['Text']).toarray()

        # Save the text features to a CSV file
        features_path = os.path.join(settings.BASE_DIR, 'dataset', 'text_features.csv')
        pd.DataFrame(text_features).to_csv(features_path, index=False)

        # Save the vectorizer to a .pkl file
        vectorizer_path = os.path.join(settings.BASE_DIR, 'model', 'tfidf_vectorizer.pkl')
        os.makedirs(os.path.dirname(vectorizer_path), exist_ok=True)
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(vectorizer, f)

        # Print the first few rows to verify
        self.stdout.write(self.style.SUCCESS(f"First 5 rows of text features:\n{text_features[:5]}"))

        self.stdout.write(self.style.SUCCESS('Text data processed, features extracted, and TfidfVectorizer saved successfully.'))