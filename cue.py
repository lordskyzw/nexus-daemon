from queue import Queue


__all__ = ["pdf_queue"]


# Define a global queue instance
pdf_queue = Queue(maxsize=10)  # You can adjust the max size as needed
