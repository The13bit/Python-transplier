#ifndef PYTHON_RUNTIME_HPP
#define PYTHON_RUNTIME_HPP

#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <stdexcept>
#include <iostream>
#include <memory>
#include <functional>
#include <algorithm>
#include <cmath>
#include <sstream>
#include <fstream>

namespace py {

// Python-like range implementation
class range {
private:
    struct iterator {
        int value;
        int step;
        
        iterator(int value, int step) : value(value), step(step) {}
        
        iterator& operator++() {
            value += step;
            return *this;
        }
        
        bool operator!=(const iterator& other) const {
            return step > 0 ? value < other.value : value > other.value;
        }
        
        int operator*() const { return value; }
    };
    
    int start_;
    int stop_;
    int step_;

public:
    range(int stop) : start_(0), stop_(stop), step_(1) {
        if (step_ == 0) throw std::invalid_argument("range() step argument must not be zero");
    }
    
    range(int start, int stop) : start_(start), stop_(stop), step_(1) {
        if (step_ == 0) throw std::invalid_argument("range() step argument must not be zero");
    }
    
    range(int start, int stop, int step) : start_(start), stop_(stop), step_(step) {
        if (step_ == 0) throw std::invalid_argument("range() step argument must not be zero");
    }
    
    iterator begin() const { return iterator(start_, step_); }
    iterator end() const { return iterator(stop_, step_); }
};

// Forward declarations
template<typename T> class list;
template<typename K, typename V> class dict;
template<typename T> class set;

// Python-like list implementation
template<typename T>
class list : public std::vector<T> {
public:
    using std::vector<T>::vector;

    void append(const T& item) {
        this->push_back(item);
    }

    T pop(int index = -1) {
        if (this->empty()) {
            throw std::out_of_range("pop from empty list");
        }
        
        if (index < 0) {
            index = this->size() + index;
        }
        
        if (index < 0 || static_cast<size_t>(index) >= this->size()) {
            throw std::out_of_range("pop index out of range");
        }
        
        T value = (*this)[index];
        this->erase(this->begin() + index);
        return value;
    }

    size_t len() const {
        return this->size();
    }
};

// Python-like dictionary implementation
template<typename K, typename V>
class dict : public std::unordered_map<K, V> {
public:
    using std::unordered_map<K, V>::unordered_map;

    V get(const K& key, const V& default_value = V()) const {
        auto it = this->find(key);
        return it != this->end() ? it->second : default_value;
    }

    list<K> keys() const {
        list<K> result;
        for (const auto& pair : *this) {
            result.append(pair.first);
        }
        return result;
    }

    list<V> values() const {
        list<V> result;
        for (const auto& pair : *this) {
            result.append(pair.second);
        }
        return result;
    }

    size_t len() const {
        return this->size();
    }
};

// Python-like set implementation
template<typename T>
class set : public std::unordered_set<T> {
public:
    using std::unordered_set<T>::unordered_set;
    
    // Set operations
    set<T> operator|(const set<T>& other) const {
        set<T> result = *this;
        result.insert(other.begin(), other.end());
        return result;
    }

    set<T> operator&(const set<T>& other) const {
        set<T> result;
        for (const auto& item : *this) {
            if (other.find(item) != other.end()) {
                result.insert(item);
            }
        }
        return result;
    }

    set<T> operator-(const set<T>& other) const {
        set<T> result;
        for (const auto& item : *this) {
            if (other.find(item) == other.end()) {
                result.insert(item);
            }
        }
        return result;
    }

    size_t len() const {
        return this->size();
    }
};

// Utility functions
template<typename Container>
size_t len(const Container& container) {
    return container.size();
}

inline void print() {
    std::cout << std::endl;
}

template<typename T>
void print(const T& arg) {
    std::cout << arg << std::endl;
}

template<typename T, typename... Args>
void print(const T& first, const Args&... args) {
    std::cout << first << " ";
    print(args...);
}

// File handling
class file {
    std::fstream fs;
    std::string mode;

public:
    file(const std::string& filename, const std::string& mode)
        : mode(mode) {
        auto flags = std::ios::in;
        if (mode == "w") {
            flags = std::ios::out | std::ios::trunc;
        } else if (mode == "a") {
            flags = std::ios::out | std::ios::app;
        }
        fs.open(filename, flags);
        if (!fs.is_open()) {
            throw std::runtime_error("Failed to open file: " + filename);
        }
    }

    void write(const std::string& data) {
        fs << data;
        fs.flush();
    }

    std::string read() {
        std::stringstream ss;
        ss << fs.rdbuf();
        return ss.str();
    }

    void close() {
        fs.close();
    }

    ~file() {
        if (fs.is_open()) {
            fs.close();
        }
    }
};

// Context manager support
template<typename T>
class ContextManager {
    T& obj;
public:
    ContextManager(T& obj) : obj(obj) {}
    T& enter() { return obj; }
    void exit() { obj.close(); }
};

// Format string implementation
template<typename... Args>
std::string format(const std::string& format_str, const Args&... args) {
    std::ostringstream ss;
    auto str_args = std::vector<std::string>{std::to_string(args)...};
    size_t arg_index = 0;
    size_t pos = 0;
    
    while ((pos = format_str.find("{}", pos)) != std::string::npos) {
        if (arg_index < str_args.size()) {
            ss << format_str.substr(0, pos) << str_args[arg_index++];
            pos += 2;
        }
    }
    
    ss << format_str.substr(pos);
    return ss.str();
}

} // namespace py

#endif // PYTHON_RUNTIME_HPP