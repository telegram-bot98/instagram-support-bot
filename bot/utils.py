import sys, time

# طباعة بطيئة (محاكاة كتابة)
def slow_typing(text, delay=0.05):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()
