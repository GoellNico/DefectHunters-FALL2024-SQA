import os
import logging
import shutil

from repo_miner import deleteRepo, makeChunks, cloneRepo, dumpContentIntoFile, getPythonCount

def main():
    # Set up a test directory and files
    test_target_dir = 'test_repo'
    test_file_path = 'test_output.txt'

    # Create a mock test directory for testing purposes
    if not os.path.exists(test_target_dir):
        os.mkdir(test_target_dir)
        with open(os.path.join(test_target_dir, 'test_script.py'), 'w') as f:
            f.write("print('Hello, World!')")

    # Initial logs
    logging.info('Starting main.py demonstration')

    # Demonstrate getPythonCount function
    logging.info('Testing getPythonCount function')
    py_count = getPythonCount(test_target_dir)
    print(f'Python file count in {test_target_dir}: {py_count}')

    # Demonstrate dumpContentIntoFile function
    logging.info('Testing dumpContentIntoFile function')
    content_size = dumpContentIntoFile('Sample content for testing.', test_file_path)
    print(f'File size of {test_file_path}: {content_size} bytes')

    # Demonstrate deleteRepo function
    logging.info('Testing deleteRepo function')
    deleteRepo(test_target_dir, 'TEST_DELETION')

    # Demonstrate makeChunks function
    logging.info('Testing makeChunks function')
    sample_list = [i for i in range(20)]  # Sample list to chunk
    chunk_size = 5
    chunks = list(makeChunks(sample_list, chunk_size))
    print(f'Chunks of size {chunk_size} from list: {chunks}')

    logging.info('main.py demonstration completed')

if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(
        filename='main_demo_forensics.log',
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] - %(message)s'
    )

    logging.info('Running main.py')
    main()
    logging.info('main.py execution finished')
