from flood_detection_model import ModelConfig, FloodDetectionModel, Trainer, predict

# Create config
config = ModelConfig()

# Initialize model
model = FloodDetectionModel(config=config)

# Create trainer
trainer = Trainer(config, model, train_data, valid_data)

# Train model
trainer.train()

# Make predictions
predictions = predict(trainer.state, model, test_data, config.batch_size)"""
Flood Detection Model for South Africa
This module implements a deep learning model that combines transformer-based processing
of time series data with CNN-based processing of satellite imagery to detect flood events.
"""

import jax
import jax.numpy as jnp
from flax import linen as nn
from dataclasses import dataclass
from typing import Tuple, Dict
import optax
from flax.training import train_state
from functools import partial
import numpy as np
from tqdm.auto import tqdm

@dataclass
class ModelConfig:
    """Configuration for the flood detection model."""
    # Model architecture
    hidden_dim: int = 256
    num_heads: int = 8
    num_layers: int = 6
    dropout: float = 0.1
    
    # Training
    batch_size: int = 32
    learning_rate: float = 1e-4
    weight_decay: float = 0.01
    num_epochs: int = 100
    
    # Data
    img_shape: Tuple[int, int, int] = (128, 128, 6)  # height, width, channels
    seed: int = 42

class FloodDetectionModel(nn.Module):
    """
    A deep learning model for flood detection that combines transformer-based processing
    of time series data with CNN-based processing of satellite imagery.
    """
    config: ModelConfig

    def __call__(self, inputs, train: bool = True):
        """
        Forward pass of the model.
        
        Args:
            inputs: Tuple of (timeseries, images)
                - timeseries: shape (batch_size, time_steps, input_dim)
                - images: shape (batch_size, height, width, channels)
            train: Whether in training mode (enables dropout)
            
        Returns:
            Logits for flood prediction, shape (batch_size, time_steps)
        """
        timeseries, images = inputs
        B, T, D = timeseries.shape  # batch_size, time_steps, input_dim
        
        # Process time series
        x_ts = nn.Dense(self.config.hidden_dim)(timeseries)
        
        # Add positional encoding for time series
        pos_encoding = self.get_positional_encoding(T, self.config.hidden_dim)
        x_ts = x_ts + pos_encoding[None, :, :]
        
        # Transformer layers for time series
        for _ in range(self.config.num_layers):
            y = nn.LayerNorm()(x_ts)
            y = nn.MultiHeadDotProductAttention(
                num_heads=self.config.num_heads
            )(y, y, deterministic=not train)
            x_ts = x_ts + y
            
            # Add feed-forward layer
            y = nn.LayerNorm()(x_ts)
            y = nn.Dense(self.config.hidden_dim * 4)(y)
            y = nn.gelu(y)
            y = nn.Dense(self.config.hidden_dim)(y)
            y = nn.Dropout(rate=self.config.dropout, deterministic=not train)(y)
            x_ts = x_ts + y
        
        # Process images
        x_img = nn.Conv(
            features=self.config.hidden_dim,
            kernel_size=(3, 3),
            padding='SAME'
        )(images)
        
        # Global average pooling for images
        x_img = jnp.mean(x_img, axis=(1, 2))  # (B, hidden_dim)
        
        # Project image features to match time series length
        x_img = nn.Dense(self.config.hidden_dim)(x_img)
        x_img = jnp.expand_dims(x_img, axis=1)  # (B, 1, hidden_dim)
        x_img = jnp.tile(x_img, (1, T, 1))      # (B, T, hidden_dim)
        
        # Combine features through addition instead of concatenation
        x = x_ts + x_img  # (B, T, hidden_dim)
        
        # Final layer norm
        x = nn.LayerNorm()(x)
        
        # Output projection
        x = nn.Dense(1)(x)
        return jnp.squeeze(x, axis=-1)
    
    def get_positional_encoding(self, length: int, depth: int) -> jnp.ndarray:
        """
        Create sinusoidal positional encoding.
        
        Args:
            length: Sequence length
            depth: Hidden dimension size
            
        Returns:
            Positional encoding of shape (length, depth)
        """
        positions = jnp.arange(length)[:, None]
        depths = jnp.arange(depth)[None, :]
        angle_rates = 1 / (10000**(2 * (depths // 2) / depth))
        angle_rads = positions * angle_rates
        
        pos_encoding = jnp.zeros_like(angle_rads)
        pos_encoding = pos_encoding.at[:, 0::2].set(jnp.sin(angle_rads[:, 0::2]))
        pos_encoding = pos_encoding.at[:, 1::2].set(jnp.cos(angle_rads[:, 1::2]))
        
        return pos_encoding

class Trainer:
    """Handles model training and evaluation."""
    
    def __init__(self, config: ModelConfig, model: nn.Module, train_data: Dict, valid_data: Dict):
        """
        Initialize trainer.
        
        Args:
            config: Model configuration
            model: The FloodDetectionModel instance
            train_data: Training data dictionary with 'timeseries', 'images', and 'labels'
            valid_data: Validation data dictionary with same structure as train_data
        """
        self.config = config
        self.model = model
        self.train_data = train_data
        self.valid_data = valid_data
        
        # Initialize training state
        rng = jax.random.PRNGKey(config.seed)
        dummy_batch = (
            jnp.ones((1, train_data['timeseries'].shape[1], train_data['timeseries'].shape[2])),
            jnp.ones((1,) + config.img_shape)
        )
        variables = model.init(rng, dummy_batch)
        
        # Create optimizer
        tx = optax.chain(
            optax.clip_by_global_norm(1.0),
            optax.adamw(
                learning_rate=optax.cosine_decay_schedule(
                    init_value=config.learning_rate,
                    decay_steps=config.num_epochs,
                    alpha=0.1
                ),
                weight_decay=config.weight_decay
            )
        )
        
        self.state = train_state.TrainState.create(
            apply_fn=model.apply,
            params=variables['params'],
            tx=tx
        )
    
    def train(self):
        """Training loop with validation."""
        for epoch in range(self.config.num_epochs):
            # Training
            with tqdm(range(0, len(self.train_data['timeseries']), self.config.batch_size),
                     desc=f"Epoch {epoch+1}/{self.config.num_epochs}") as pbar:
                
                for i in pbar:
                    batch_idx = slice(i, i + self.config.batch_size)
                    batch = {
                        'timeseries': self.train_data['timeseries'][batch_idx],
                        'images': self.train_data['images'][batch_idx],
                        'labels': self.train_data['labels'][batch_idx]
                    }
                    
                    # Training step
                    self.state, metrics = self.train_step(batch)
                    pbar.set_postfix({'loss': f"{metrics['loss']:.4f}",
                                   'acc': f"{metrics['accuracy']:.4f}"})
            
            # Validation
            valid_metrics = self.evaluate()
            print(f"\nValidation - Loss: {valid_metrics['loss']:.4f}, "
                  f"Acc: {valid_metrics['accuracy']:.4f}")
    
    @partial(jax.jit, static_argnums=(0,))
    def train_step(self, batch):
        """Single training step."""
        def loss_fn(params):
            logits = self.model.apply(
                {'params': params},
                (batch['timeseries'], batch['images']),
                train=True
            )
            loss = optax.sigmoid_binary_cross_entropy(logits, batch['labels']).mean()
            return loss, logits
        
        (loss, logits), grads = jax.value_and_grad(loss_fn, has_aux=True)(self.state.params)
        state = self.state.apply_gradients(grads=grads)
        
        # Compute metrics
        metrics = {
            'loss': loss,
            'accuracy': jnp.mean((jax.nn.sigmoid(logits) > 0.5) == batch['labels'])
        }
        
        return state, metrics
    
    def evaluate(self):
        """Evaluate on validation set."""
        metrics_list = []
        
        for i in range(0, len(self.valid_data['timeseries']), self.config.batch_size):
            batch_idx = slice(i, i + self.config.batch_size)
            batch = {
                'timeseries': self.valid_data['timeseries'][batch_idx],
                'images': self.valid_data['images'][batch_idx],
                'labels': self.valid_data['labels'][batch_idx]
            }
            
            logits = self.model.apply(
                {'params': self.state.params},
                (batch['timeseries'], batch['images']),
                train=False
            )
            
            loss = optax.sigmoid_binary_cross_entropy(logits, batch['labels']).mean()
            accuracy = jnp.mean((jax.nn.sigmoid(logits) > 0.5) == batch['labels'])
            
            metrics_list.append({'loss': loss, 'accuracy': accuracy})
        
        # Average metrics
        return {
            k: float(np.mean([m[k] for m in metrics_list]))
            for k in metrics_list[0].keys()
        }

def predict(model_state: train_state.TrainState, 
           model: FloodDetectionModel,
           test_data: Dict,
           batch_size: int) -> jnp.ndarray:
    """
    Generate predictions for test data.
    
    Args:
        model_state: Trained model state
        model: FloodDetectionModel instance
        test_data: Test data dictionary with 'timeseries' and 'images'
        batch_size: Batch size for predictions
        
    Returns:
        Array of predictions
    """
    predictions = []
    
    for i in range(0, len(test_data['timeseries']), batch_size):
        batch_idx = slice(i, i + batch_size)
        batch = {
            'timeseries': test_data['timeseries'][batch_idx],
            'images': test_data['images'][batch_idx]
        }
        
        logits = model.apply(
            {'params': model_state.params},
            (batch['timeseries'], batch['images']),
            train=False
        )
        predictions.append(jax.nn.sigmoid(logits))
    
    return jnp.concatenate(predictions, axis=0)
