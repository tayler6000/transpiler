import sys

if __name__ == "__main__":
    print("Hello, World!", "Hello, Rust!", 8, sep="*", end="\r\n")
    print(42, end="?\n")
    x = input("> ")
    print(x)
    sys.exit()
