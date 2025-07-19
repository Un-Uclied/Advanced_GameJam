#파이썬엔 포인터가 없기에 wrapper로 변경

class IntValue:
    def __init__(self, value):
        self.value = value

class StringValue:
    def __init__(self, value):
        self.value = value