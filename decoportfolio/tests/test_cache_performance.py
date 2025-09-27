import time
import requests

def test_api_performance():
    url = "http://127.0.0.1:8000/api/portfolio-items/"

    print("Testing API performance...")

    # Test 5 requests
    times = []
    for i in range(5):
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()

        request_time = (end_time - start_time) * 1000 # Convert to milliseconds
        times.append(request_time)

        print(f"Request {i + 1}: {request_time:.2f}ms - Status: {response.status_code}")

    avg_time = sum(times) / len(times)
    print(f"\nAverage request time: {avg_time:.2f}ms")

    if avg_time < 100:
        print("Excellent performance! Cache is working!")
    elif avg_time < 500:
        print("Good performance! Cache is working well!")
    else:
        print("Performance could be better. Check cache configuration.")

if __name__ == "__main__":
    test_api_performance()