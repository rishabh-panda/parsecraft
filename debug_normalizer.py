from parsecraft.normalization.normalizer import Normalizer
n = Normalizer()
test = '   {"key":   "value"}   '
print("Input:", repr(test))
result = n.normalize(test)
print("Output:", repr(result))
print("Expected:", repr('{"key":   "value"}'))