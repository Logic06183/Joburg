"""
Script to train and run the flood detection model.
"""

import os
import sys
import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import jax
import jax.numpy as jnp
import gc  # Add garbage collection
import tempfile
from flood_detection_model import ModelConfig, FloodDetectionModel, Trainer, predict

def create_memmap_array(shape, dtype, filename):
    """Create a memory-mapped array file."""
    return np.memmap(filename, dtype=dtype, mode='w+', shape=shape)

def load_data():
    """Load and preprocess the data."""
    try:
        start_time = time.time()
        
        # Load CSV files
        print("Loading CSV files...")
        csv_start = time.time()
        train_df = pd.read_csv('Train.csv')
        test_df = pd.read_csv('Test.csv')
        print(f"CSV files loaded in {time.time() - csv_start:.2f} seconds")
        print(f"Train shape: {train_df.shape}, Test shape: {test_df.shape}")
        
        # Load time series data
        print("\nProcessing time series data...")
        ts_start = time.time()
        def process_timeseries(df):
            grouped = df.groupby('event_id')['precipitation'].apply(list).reset_index()
            max_len = 730
            padded = np.array([seq + [0] * (max_len - len(seq)) for seq in grouped['precipitation']], dtype=np.float32)
            return padded

        train_ts = process_timeseries(train_df)
        test_ts = process_timeseries(test_df)
        print(f"Time series processing completed in {time.time() - ts_start:.2f} seconds")
        print(f"Train time series shape: {train_ts.shape}, Test time series shape: {test_ts.shape}")
        
        # Process labels
        print("\nProcessing labels...")
        label_start = time.time()
        train_labels = train_df.groupby('event_id')['label'].first().values
        print(f"Labels processed in {time.time() - label_start:.2f} seconds")
        
        # Create temporary files for memory mapping
        temp_dir = tempfile.gettempdir()
        train_mmap_file = os.path.join(temp_dir, 'train_images.mmap')
        test_mmap_file = os.path.join(temp_dir, 'test_images.mmap')
        
        # Process images one at a time using memory mapping
        print("\nProcessing images...")
        img_proc_start = time.time()
        
        # Create memory-mapped arrays
        train_shape = (len(train_df['event_id'].unique()), 128, 128, 6)
        test_shape = (len(test_df['event_id'].unique()), 128, 128, 6)
        
        train_images = create_memmap_array(train_shape, np.float32, train_mmap_file)
        test_images = create_memmap_array(test_shape, np.float32, test_mmap_file)
        
        # Load and process images one at a time
        images_npz = np.load('composite_images.npz')
        
        # Process train images
        train_event_ids = train_df['event_id'].unique()
        for idx, event_id in enumerate(train_event_ids):
            if idx % 100 == 0:
                print(f"Processing train image {idx+1}/{len(train_event_ids)}", end='\r')
                gc.collect()
            
            base_id = event_id.split('_X_')[0]
            try:
                img = images_npz[base_id]
                img = img.astype(np.float32) / 65535.0
            except KeyError:
                print(f"\nWarning: Image not found for event {event_id}")
                img = np.zeros((128, 128, 6), dtype=np.float32)
            
            train_images[idx] = img
        print()  # New line after progress
        
        # Process test images
        test_event_ids = test_df['event_id'].unique()
        for idx, event_id in enumerate(test_event_ids):
            if idx % 100 == 0:
                print(f"Processing test image {idx+1}/{len(test_event_ids)}", end='\r')
                gc.collect()
            
            base_id = event_id.split('_X_')[0]
            try:
                img = images_npz[base_id]
                img = img.astype(np.float32) / 65535.0
            except KeyError:
                print(f"\nWarning: Image not found for event {event_id}")
                img = np.zeros((128, 128, 6), dtype=np.float32)
            
            test_images[idx] = img
        print()  # New line after progress
        
        images_npz.close()
        
        print(f"Image processing completed in {time.time() - img_proc_start:.2f} seconds")
        print(f"Train images shape: {train_images.shape}, Test images shape: {test_images.shape}")
        
        # Split training data into train and validation
        print("\nSplitting data...")
        split_start = time.time()
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
        print(f"Data splitting completed in {time.time() - split_start:.2f} seconds")
        
        return train_data, valid_data, test_data
        
    except Exception as e:
        print("Error loading data:", str(e))
        raise

def main():
    try:
        # Load data
        print("Loading data...")
        train_data, valid_data, test_data = load_data()
        
        # Create config
        print("Creating model configuration...")
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
        
    except Exception as e:
        print(f"Error during training: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
