from core_service import start_watcher
import threading
from extraction_engine import process_queue

def start_core_service():
    """Starts the core service to watch the directory."""
    print("Starting Core Service...")
    start_watcher()  # Use start_watcher here

def start_extraction_service():
    """Starts the extraction service to process the queue."""
    print("Starting Extraction Engine...")
    process_queue()

if __name__ == "__main__":
    print("Starting the PDF Processing System...")

    # Create and start threads for the services
    core_thread = threading.Thread(target=start_core_service, daemon=True)
    extraction_thread = threading.Thread(target=start_extraction_service, daemon=True)

    core_thread.start()
    extraction_thread.start()

    # Keep the main thread alive while other threads run
    core_thread.join()
    extraction_thread.join()
