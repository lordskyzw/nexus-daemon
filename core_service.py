from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from cue import pdf_queue
import time

queue = pdf_queue

class DirectoryWatcher(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith('.pdf'):
            print(f"New file detected: {event.src_path}")
            queue.put(event.src_path)

def start_watcher(directory='unprocessed'):
    event_handler = DirectoryWatcher()
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watcher()
