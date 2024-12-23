"""
Script to train and run the flood detection model.
"""

import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from flood_detection_model import ModelConfig, FloodDetectionModel, Trainer, predict

def load_data():
    """Load and preprocess the data."""
    # Load CSV files
    train_df = pd.read_csv('Train.csv')
    test_df = pd.read_csv('Test.csv')
    
    # Load image data
    images = np.load('composite_images.npz')
    
    # Preprocess time series data
    def process_timeseries(df):
        # Group by event_id and create time series features
        grouped = df.groupby('event_id')['precipitation'].apply(list).reset_index()
        # Pad sequences to max length
        max_len = 730  # As per your data
        padded = np.array([seq + [0] * (max_len - len(seq)) for seq in grouped['precipitation']])
        return padded

    # Process train and test data
    train_ts = process_timeseries(train_df)
    test_ts = process_timeseries(test_df)
    
    # Process labels for training data
    train_labels = train_df.groupby('event_id')['label'].first().values
    
    # Process images
    train_images = []
    test_images = []
    for event_id in train_df['event_id'].unique():
        base_id = event_id.split('_X_')[0]  # Remove '_X_n' suffix
        train_images.append(images[base_id])
    for event_id in test_df['event_id'].unique():
        base_id = event_id.split('_X_')[0]  # Remove '_X_n' suffix
        test_images.append(images[base_id])
    
    train_images = np.array(train_images)
    test_images = np.array(test_images)
    
    # Split training data into train and validation
    train_indices, val_indices = train_test_split(
        np.arange(len(train_ts)), 
        test_size=0.1, 
        random_state=42
    )
    
    # Create data dictionaries
    train_data = {
        'timeseries': train_ts[train_indices],
        'images': train_images[train_indices],
        'labels': train_labels[train_indices]
    }
    
    valid_data = {
        'timeseries': train_ts[val_indices],
        'images': train_images[val_indices],
        'labels': train_labels[val_indices]
    }
    
    test_data = {
        'timeseries': test_ts,
        'images': test_images
    }
    
    return train_data, valid_data, test_data

def main():
    # Load data
    print("Loading data...")
    train_data, valid_data, test_data = load_data()
    
    # Create config
    config = ModelConfig(
        hidden_dim=256,
        num_heads=8,
        num_layers=6,
        dropout=0.1,
        batch_size=32,
        num_epochs=100
    )
    
    # Initialize model
    print("\nInitializing model...")
    model = FloodDetectionModel(config=config)
    
    # Create trainer
    print("Setting up trainer...")
    trainer = Trainer(config, model, train_data, valid_data)
    
    # Train model
    print("\nStarting training...")
    trainer.train()
    
    # Make predictions
    print("\nMaking predictions on test set...")
    predictions = predict(trainer.state, model, test_data, config.batch_size)
    
    # Save predictions
    print("Saving predictions...")
    submission_df = pd.read_csv('SampleSubmission.csv')
    submission_df['label'] = predictions
    submission_df.to_csv('submission.csv', index=False)
    
    print("\nDone! Predictions saved to 'submission.csv'")

if __name__ == "__main__":
    main()
