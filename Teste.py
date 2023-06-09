for c in range(0, 1000000):
    num = 9*c + 1
    while num >= 1:
        if num % 2 == 0:
            num /= 2
        else:
            break
        if num == 1:
            print(9*c + 1, 16*c + 1)
        