def add(a, b):
    return a + b


if __name__ == "__main__":
    a = float(input("请输入第一个数字: "))
    b = float(input("请输入第二个数字: "))
    result = add(a, b)
    print(f"{a} + {b} = {result}")
