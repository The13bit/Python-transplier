my_frozenset = frozenset([1, 2, 3])  # Frozen Set
# Basic Operations
x:float = 10 + 5  # Addition
y = 10 - 5  # Subtraction
z = 10 * 5  # Multiplication 
a = 10 / 5  # Division
b = 10 // 3 # Floor division
c = 10 % 3  # Modulo
d = 2 ** 3  # Exponentiation

# Data Structures
my_list = [1, 2, 3]  # List
my_tuple = (1, 2, 3)  # Tuple
my_dict = {'a': 1, 'b': 2}  # Dictionarypython ast follow import
my_set = {1, 2, 3}  # Set


# Control Flow
if x > 0:
    print("Positive")
elif x < 0:
    print("Negative")
else:
    print("Zero")

# Loops
for i in range(5):
    print(i)
for i in range(0,5,2):
    print(i)

a=[1,2,3,4]
for i in a:
    print(i)

while x > 0:
    x -= 1

# List Comprehension
squares = [x**2 for x in range(10)]

# Generator Expression
gen = (x**2 for x in range(10))

# Functions
def greet(name: str) -> str:
    return f"Hello {name}"

# Lambda Function
square = lambda x: x**2

# Class Definition
class Person:
    def __init__(self, name):
        self.name = name
    
    def say_hi(self):
        return f"Hi, I'm {self.name}"

# # Exception Handling
# try:
#     result = 10/0
# except ZeroDivisionError:
#     print("Cannot divide by zero")
# finally:
#     print("Cleanup code")

# # Context Manager
# with open('example.txt', 'w') as f:
#     f.write('Hello')



# Decorators
# def my_decorator(func):
#     def wrapper():
#         print("Before")
#         func()
#         print("After")
#     return wrapper

# @my_decorator
# def say_hello():
#     print("Hello")

# Sets Operations
set1 = {1, 2, 3}
set2 = {3, 4, 5}
union = set1 | set2
intersection = set1 & set2
difference = set1 - set2

# Dictionary Comprehension
square_dict = {x: x**2 for x in range(5)}

def calculate_stats(numbers):
    """Calculate basic statistics for a list of numbers."""
    total = 0
    count = len(numbers)
    
    for num in numbers:
        total += num
    
    average = total / count
    
    if average > 50:
        result = "High"
    else:
        result = "Low"
    
    stats = {
        "total": total,
        "average": average,
        "count": count,
        "category": result
    }
    
    return stats

# Test the function
test_numbers = [10, 20, 30, 40, 50]
result = calculate_stats(test_numbers)
print(f"Statistics: {result}")


