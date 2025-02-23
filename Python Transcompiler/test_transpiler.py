import os
import subprocess
from transpiler import transpile_file

def compile_cpp(cpp_file: str, output_file: str) -> bool:
    """Compile C++ code using g++."""
    try:
        cmd = [
            "g++",
            "-std=c++17",      # Use C++17 for advanced features
            "-I", ".",         # Include current directory for runtime.hpp
            "-Wno-write-strings",  # Suppress string literal warnings
            cpp_file,
            "-o", output_file
        ]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Compilation output:")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("\nCompilation failed:")
        print(e.stderr)
        return False

def transpile_and_test():
    
    # Step 3: Transpile Test_code.py to C++
    print("Transpiling Test_code.py to C++...")
    input_file = os.path.join("Python Transcompiler", "Test_code.py")
    cpp_file = os.path.join("Python Transcompiler", "test_code.cpp")
    
    try:
        transpile_file(input_file, cpp_file)
        print("✓ Transpilation successful")
        
        # Step 4: Compile all C++ files together
        print("\nCompiling generated C++ code...")
        exe_file = os.path.join("Python Transcompiler", "test_code")
        
        # Compile imports.cpp first to create object file
        if not compile_cpp(
            os.path.join("Python Transcompiler", "imports.cpp"),
            os.path.join("Python Transcompiler", "imports.o")
        ):
            print("✗ Failed to compile imports.cpp")
            return False
            
        # Compile and link everything together
        cmd = [
            "g++",
            "-std=c++17",
            "-I", "Python Transcompiler",
            cpp_file,
            os.path.join("Python Transcompiler", "imports.o"),
            "-o", exe_file
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✓ Compilation successful")
            
            # Step 5: Run the compiled program
            print("\nRunning the compiled program:")
            print("-" * 40)
            subprocess.run([exe_file])
            print("-" * 40)
            print("✓ Program executed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print("\nLinking failed:")
            print(e.stderr)
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = transpile_and_test()
    exit(0 if success else 1)