# test_js_stable.py
import js, threading

def task(n):
    print(js.run_code(f"1 + {n}"))

threads = [threading.Thread(target=task, args=(i,)) for i in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()
