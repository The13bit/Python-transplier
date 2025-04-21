import random
import math
import re
from typing import List
import time
import numpy as np
import mini
from mini.PUDA import met, to_c
import mini.PUDA
from numba import jit
DEBUG=True
@to_c(dbg=DEBUG)

def matrix_multiply(
    A: List[List[float]],
    B: List[List[float]],
    res: List[List[float]],
    rows_A: int,
    cols_A: int,
    cols_B: int,
):
    
    for i in range(rows_A):
        for j in range(cols_B):
            for k in range(cols_A):
                res[i][j] += A[i][k] * B[k][j]
    return res
class NeuralNetwork:
    def __init__(self, layer_sizes):
        """
        Initialize neural network with configurable layers
        layer_sizes: List of integers specifying number of neurons in each layer
                     Example: [2, 3, 2, 1] for 4-layer network
        """
        self.layer_sizes = layer_sizes
        self.num_layers = len(layer_sizes)
        
        # Initialize weights and biases for each layer
        self.weights = []
        self.biases = []
        for i in range(1, self.num_layers):
            input_size = layer_sizes[i-1]
            output_size = layer_sizes[i]
            
            # Initialize weights with He initialization
            weights = [[random.uniform(-1, 1) * math.sqrt(2/input_size) 
                       for _ in range(output_size)] 
                      for _ in range(input_size)]
            
            # Initialize biases with zeros
            biases = [0.0 for _ in range(output_size)]
            
            self.weights.append(weights)
            self.biases.append(biases)

    def sigmoid(self, x):
        return 1 / (1 + math.exp(-x))

    def sigmoid_derivative(self, x):
        return x * (1 - x)

    def forward(self, X):
        """Forward pass through all layers"""
        # Ensure input is in matrix format
        activation = X if isinstance(X[0], list) else [X]
        self.activations = [activation]  # Store all layer activations
        
        for layer_idx in range(self.num_layers - 1):
            # Get current layer parameters
            weights = self.weights[layer_idx]
            biases = self.biases[layer_idx]
            
            # Calculate layer input
            rows_A = len(activation)
            cols_A = len(activation[0])
            cols_B = len(weights[0])
            layer_input = matrix_multiply(activation, weights,[[0.0 for _ in range(cols_B)] for _ in range(rows_A)], rows_A, cols_A, cols_B)
            
            # Apply activation function (sigmoid for all layers)
            activation = self.apply_activation(layer_input, biases)
            
            # Store activation for backpropagation
            self.activations.append(activation)
            
        return activation

    def backward(self, X, y, learning_rate):
        """Backpropagation through all layers"""
        # Calculate initial error
        output = self.activations[-1]
        error = self.calculate_error_derivative(output, y)
        
        # Backpropagate error through layers
        for layer_idx in reversed(range(self.num_layers - 1)):
            # Get current layer parameters
            if not DEBUG: 
                met()
            weights = self.weights[layer_idx]
            prev_activation = self.activations[layer_idx]
            
            # Calculate delta for current layer
            delta = self.calculate_delta(error, layer_idx)
            
            # Update weights and biases
            self.update_parameters(layer_idx, prev_activation, delta, learning_rate)
            
            # Propagate error backward
            error = self.propagate_error_backward(delta, weights)

    def train(self, X, y, epochs, learning_rate):
        """Train the network using gradient descent"""
        prev=0
        for epoch in range(epochs):
            # Forward pass
            output = self.forward(X)
            
            # Backward pass
            self.backward(X, y, learning_rate)
            
            # Calculate and print loss
            if epoch!=0 and epoch % 1000 == 0:
                loss = self.calculate_loss(output, y)
                
                print(f"Epoch {epoch}, Loss: {loss:.6f}")
                if DEBUG==True:
                    print("Overhead:",mini.PUDA.overhead[0]-prev)
                    prev=mini.PUDA.overhead[0]



    def apply_activation(self, matrix, biases):
        """Apply sigmoid activation to matrix with biases"""
        return [[self.sigmoid(val + biases[j]) 
                for j, val in enumerate(row)] 
               for row in matrix]

    def calculate_error_derivative(self, output, y):
        """Calculate derivative of loss function (MSE)"""
        return [[output[i][j] - y[i][j] 
                for j in range(len(output[0]))] 
               for i in range(len(output))]

    def calculate_delta(self, error, layer_idx):
        """Calculate delta for current layer"""
        activation_deriv = [[self.sigmoid_derivative(val) 
                           for val in row] 
                          for row in self.activations[layer_idx+1]]
        return [[error[i][j] * activation_deriv[i][j] 
                for j in range(len(error[0]))] 
               for i in range(len(error))]

    def update_parameters(self, layer_idx, prev_activation, delta, lr):
        """Update weights and biases for current layer"""
        # Calculate weight gradients
        prev_activation_t = self.transpose(prev_activation)
        rows_A = len(prev_activation_t)
        cols_A = len(prev_activation_t[0])
        cols_B = len(delta[0])
        result = np.zeros((rows_A,cols_B),dtype=np.float32).tolist() #[[0.0 for _ in range(cols_B)] for _ in range(rows_A)]
        weight_gradients = matrix_multiply(prev_activation_t, delta,result, rows_A, cols_A, cols_B)
        
        # Update weights
        for i in range(len(self.weights[layer_idx])):
            for j in range(len(self.weights[layer_idx][0])):
                self.weights[layer_idx][i][j] -= lr * weight_gradients[i][j]
        
        # Update biases
        for j in range(len(self.biases[layer_idx])):
            bias_grad = sum(delta[i][j] for i in range(len(delta)))
            self.biases[layer_idx][j] -= lr * bias_grad

    def propagate_error_backward(self, delta, weights):
        """Propagate error to previous layer"""
        weights_t = self.transpose(weights)
        rows_A = len(delta)
        cols_A = len(delta[0])
        cols_B = len( weights_t[0])
        result = np.zeros((rows_A,cols_B),dtype=np.float32).tolist()
        
        return matrix_multiply(delta, weights_t,result, rows_A, cols_A, cols_B)

    def transpose(self, matrix):
        """Matrix transposition"""
        return list(map(list, zip(*matrix)))

    def calculate_loss(self, output, y):
        """Calculate mean squared error"""
        return sum((output[i][j] - y[i][j])**2 
                  for i in range(len(output)) 
                  for j in range(len(output[0]))) / len(output)

    def predict(self, X):
        """Make predictions"""
        output = self.forward(X)
        return output

# Example usage with 4-layer network (input: 2, hidden: 3, hidden: 2, output: 1)
if __name__ == "__main__":
    # XOR dataset
    X = [[0, 0], [0, 1], [1, 0], [1, 1]]
    y = [[0], [1], [1], [0]]

    # Create network with layer sizes [input, hidden1, hidden2, output]
    nn = NeuralNetwork([2, 32,64, 1])
    start=time.time()
    # Train network
    nn.train(X, y, epochs=2000, learning_rate=0.1)
    print("Time Taken:",time.time()-start)
    # Test predictions
    print("\nPredictions:")
    for x in X:
        pred = nn.predict([x])[0][0]
        print(f"{x} -> {pred}")